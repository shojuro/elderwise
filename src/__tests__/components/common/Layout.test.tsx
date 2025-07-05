import React from 'react';
import { render, screen } from '@testing-library/react';
import { Layout, ElderlyLayout, FamilyLayout, AuthLayout, ModalLayout } from '../../../components/common/Layout';
import { useAppStore } from '../../../store';

// Mock dependencies
jest.mock('../../../store', () => ({
  useAppStore: jest.fn(() => ({
    user: { id: 'test-user' },
    preferences: { theme: 'default' }
  }))
}));

jest.mock('../../../components/common/Navigation', () => ({
  TopNavigation: ({ title, subtitle }: any) => (
    <div data-testid="top-nav">
      {title && <h1>{title}</h1>}
      {subtitle && <p>{subtitle}</p>}
    </div>
  ),
  BottomNavigation: () => <div data-testid="bottom-nav">Bottom Nav</div>
}));

jest.mock('framer-motion', () => ({
  motion: {
    main: ({ children, ...props }: any) => <main {...props}>{children}</main>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  }
}));

describe('Layout Component', () => {
  const mockUseAppStore = useAppStore as jest.MockedFunction<typeof useAppStore>;

  beforeEach(() => {
    mockUseAppStore.mockReturnValue({
      user: { id: 'test-user', name: 'Test User' },
      preferences: { theme: 'default' },
    } as any);
  });

  it('renders children', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('shows bottom navigation by default when user is logged in', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    );

    expect(screen.getByTestId('bottom-nav')).toBeInTheDocument();
  });

  it('hides bottom navigation when showNavigation is false', () => {
    render(
      <Layout showNavigation={false}>
        <div>Test content</div>
      </Layout>
    );

    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('hides bottom navigation when user is not logged in', () => {
    mockUseAppStore.mockReturnValue({
      user: null,
      preferences: { theme: 'default' },
    } as any);

    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    );

    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('shows top navigation when showTopNav is true and title is provided', () => {
    render(
      <Layout showTopNav={true} title="Test Title" subtitle="Test Subtitle">
        <div>Test content</div>
      </Layout>
    );

    expect(screen.getByTestId('top-nav')).toBeInTheDocument();
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
  });

  it('does not show top navigation when showTopNav is false', () => {
    render(
      <Layout showTopNav={false} title="Test Title">
        <div>Test content</div>
      </Layout>
    );

    expect(screen.queryByTestId('top-nav')).not.toBeInTheDocument();
  });

  it('applies high-contrast theme when preference is set', () => {
    mockUseAppStore.mockReturnValue({
      user: { id: 'test-user' },
      preferences: { theme: 'high-contrast' },
    } as any);

    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    );

    const container = screen.getByText('Test content').closest('.min-h-screen');
    expect(container).toHaveClass('contrast-more');
  });

  it('applies custom className', () => {
    render(
      <Layout className="custom-class">
        <div>Test content</div>
      </Layout>
    );

    const main = screen.getByRole('main');
    expect(main).toHaveClass('custom-class');
  });

  it('applies fullHeight styles when fullHeight is true', () => {
    render(
      <Layout fullHeight={true}>
        <div>Test content</div>
      </Layout>
    );

    const main = screen.getByRole('main');
    expect(main).toHaveClass('h-screen');
    expect(main).not.toHaveClass('min-h-screen');
  });

  it('applies correct padding classes', () => {
    const { rerender } = render(
      <Layout showNavigation={true} showTopNav={true}>
        <div>Test content</div>
      </Layout>
    );

    let main = screen.getByRole('main');
    expect(main).toHaveClass('pb-20'); // Bottom padding for navigation
    expect(main).toHaveClass('pt-0'); // No top padding with top nav

    rerender(
      <Layout showNavigation={false} showTopNav={false}>
        <div>Test content</div>
      </Layout>
    );

    main = screen.getByRole('main');
    expect(main).not.toHaveClass('pb-20');
    expect(main).toHaveClass('pt-safe');
  });

  it('has correct accessibility attributes', () => {
    render(
      <Layout>
        <div>Test content</div>
      </Layout>
    );

    const main = screen.getByRole('main');
    expect(main).toHaveAttribute('id', 'main-content');
    expect(main).toHaveAttribute('tabIndex', '-1');
  });
});

describe('ElderlyLayout Component', () => {
  it('renders with proper settings for elderly users', () => {
    render(
      <ElderlyLayout title="Elderly View">
        <div>Elderly content</div>
      </ElderlyLayout>
    );

    expect(screen.getByText('Elderly content')).toBeInTheDocument();
    expect(screen.getByTestId('top-nav')).toBeInTheDocument();
    expect(screen.getByTestId('bottom-nav')).toBeInTheDocument();
    
    const main = screen.getByRole('main');
    expect(main).toHaveClass('text-2xl'); // Larger text for elderly
  });

  it('does not show top nav when no title', () => {
    render(
      <ElderlyLayout>
        <div>Elderly content</div>
      </ElderlyLayout>
    );

    expect(screen.queryByTestId('top-nav')).not.toBeInTheDocument();
  });
});

describe('FamilyLayout Component', () => {
  it('renders with all family-specific props', () => {
    const mockOnBack = jest.fn();
    const rightAction = <button>Action</button>;

    render(
      <FamilyLayout
        title="Family View"
        subtitle="Subtitle"
        showBack={true}
        onBack={mockOnBack}
        rightAction={rightAction}
      >
        <div>Family content</div>
      </FamilyLayout>
    );

    expect(screen.getByText('Family content')).toBeInTheDocument();
    expect(screen.getByText('Family View')).toBeInTheDocument();
    expect(screen.getByText('Subtitle')).toBeInTheDocument();
    expect(screen.getByTestId('bottom-nav')).toBeInTheDocument();
  });
});

describe('AuthLayout Component', () => {
  it('renders without navigation', () => {
    render(
      <AuthLayout>
        <div>Auth content</div>
      </AuthLayout>
    );

    expect(screen.getByText('Auth content')).toBeInTheDocument();
    expect(screen.queryByTestId('top-nav')).not.toBeInTheDocument();
    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('applies centering styles', () => {
    render(
      <AuthLayout className="custom-auth">
        <div>Auth content</div>
      </AuthLayout>
    );

    const main = screen.getByRole('main');
    expect(main).toHaveClass('flex', 'items-center', 'justify-center', 'custom-auth');
    expect(main).toHaveClass('h-screen');
  });
});

describe('ModalLayout Component', () => {
  it('renders as a full-screen modal', () => {
    render(
      <ModalLayout title="Modal Title">
        <div>Modal content</div>
      </ModalLayout>
    );

    expect(screen.getByText('Modal content')).toBeInTheDocument();
    expect(screen.getByText('Modal Title')).toBeInTheDocument();
    
    const modalContainer = screen.getByText('Modal content').closest('.fixed');
    expect(modalContainer).toHaveClass('fixed', 'inset-0', 'z-50');
  });

  it('shows top navigation with back button', () => {
    const mockOnClose = jest.fn();
    
    render(
      <ModalLayout title="Modal Title" onClose={mockOnClose}>
        <div>Modal content</div>
      </ModalLayout>
    );

    expect(screen.getByTestId('top-nav')).toBeInTheDocument();
  });

  it('applies correct padding with title', () => {
    render(
      <ModalLayout title="Modal Title">
        <div>Modal content</div>
      </ModalLayout>
    );

    const contentContainer = screen.getByText('Modal content').parentElement;
    expect(contentContainer).toHaveClass('pt-16');
  });

  it('applies safe padding without title', () => {
    render(
      <ModalLayout>
        <div>Modal content</div>
      </ModalLayout>
    );

    const contentContainer = screen.getByText('Modal content').parentElement;
    expect(contentContainer).toHaveClass('pt-safe');
    expect(contentContainer).not.toHaveClass('pt-16');
  });

  it('applies custom className', () => {
    render(
      <ModalLayout className="custom-modal">
        <div>Modal content</div>
      </ModalLayout>
    );

    const modalContainer = screen.getByText('Modal content').closest('.fixed');
    expect(modalContainer).toHaveClass('custom-modal');
  });
});
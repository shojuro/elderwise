import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Modal } from '../../../components/common/Modal';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('Modal Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    document.body.style.overflow = '';
  });

  afterEach(() => {
    document.body.style.overflow = '';
  });

  it('renders when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('renders with title', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Test Modal')).toHaveAttribute('id', 'modal-title');
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby', 'modal-title');
  });

  it('renders close button by default', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    expect(closeButton).toBeInTheDocument();
  });

  it('hides close button when showCloseButton is false', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} showCloseButton={false}>
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.queryByRole('button', { name: 'Close modal' })).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    // Click on backdrop (the outer div with opacity)
    const backdrop = document.querySelector('.bg-black.bg-opacity-50');
    expect(backdrop).toBeInTheDocument();
    fireEvent.click(backdrop!);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on backdrop click when closeOnBackdrop is false', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} closeOnBackdrop={false}>
        <p>Modal content</p>
      </Modal>
    );

    const backdrop = document.querySelector('.bg-black.bg-opacity-50');
    fireEvent.click(backdrop!);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('closes on Escape key press', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on Escape when closeOnEscape is false', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} closeOnEscape={false}>
        <p>Modal content</p>
      </Modal>
    );

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('applies correct size classes', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={mockOnClose} size="sm">
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.getByRole('dialog')).toHaveClass('max-w-sm');

    rerender(
      <Modal isOpen={true} onClose={mockOnClose} size="md">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toHaveClass('max-w-md');

    rerender(
      <Modal isOpen={true} onClose={mockOnClose} size="lg">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toHaveClass('max-w-lg');

    rerender(
      <Modal isOpen={true} onClose={mockOnClose} size="xl">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toHaveClass('max-w-xl');

    rerender(
      <Modal isOpen={true} onClose={mockOnClose} size="full">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toHaveClass('max-w-none', 'w-full', 'h-full');
  });

  it('applies custom className', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} className="custom-modal">
        <p>Modal content</p>
      </Modal>
    );

    expect(screen.getByRole('dialog')).toHaveClass('custom-modal');
  });

  it('prevents body scroll when open', () => {
    const { rerender } = render(
      <Modal isOpen={false} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('');

    rerender(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('hidden');

    rerender(
      <Modal isOpen={false} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('unset');
  });

  it('cleans up body scroll on unmount', () => {
    const { unmount } = render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('hidden');

    unmount();

    expect(document.body.style.overflow).toBe('unset');
  });

  it('removes event listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');

    const { unmount } = render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
    removeEventListenerSpy.mockRestore();
  });

  it('has proper ARIA attributes', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Accessible Modal">
        <p>Modal content</p>
      </Modal>
    );

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-modal', 'true');
    expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');
  });

  it('does not have aria-labelledby when no title', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose}>
        <p>Modal content</p>
      </Modal>
    );

    const modal = screen.getByRole('dialog');
    expect(modal).not.toHaveAttribute('aria-labelledby');
  });

  it('applies different padding when header is present', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="With Header">
        <p>Modal content</p>
      </Modal>
    );

    // With header, content should have p-6
    let contentDiv = screen.getByText('Modal content').parentElement;
    expect(contentDiv).toHaveClass('p-6');

    // Without header or close button, content should have p-8
    rerender(
      <Modal isOpen={true} onClose={mockOnClose} showCloseButton={false}>
        <p>Modal content</p>
      </Modal>
    );

    contentDiv = screen.getByText('Modal content').parentElement;
    expect(contentDiv).toHaveClass('p-8');
  });
});
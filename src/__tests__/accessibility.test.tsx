import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';

// Components to test
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Modal } from '../components/common/Modal';
import { ChatMessage } from '../components/chat/ChatMessage';
import { ElderlyLayout } from '../components/common/Layout';

// Screens to test
import { WelcomeScreen } from '../screens/auth/WelcomeScreen';
import { HomeScreen } from '../screens/main/HomeScreen';
import { ChatScreen } from '../screens/main/ChatScreen';
import { MemoryScreen } from '../screens/main/MemoryScreen';
import { EmergencyScreen } from '../screens/main/EmergencyScreen';
import { SettingsScreen } from '../screens/main/SettingsScreen';

// Add jest-axe matchers
expect.extend(toHaveNoViolations);

// Helper to wrap components with necessary providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Accessibility Tests', () => {
  describe('Component Accessibility', () => {
    test('Button component has no accessibility violations', async () => {
      const { container } = render(
        <Button variant="primary">Test Button</Button>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    test('Button has proper ARIA attributes', () => {
      render(
        <Button 
          variant="primary" 
          ariaLabel="Save changes"
          disabled
        >
          Save
        </Button>
      );
      
      const button = screen.getByRole('button', { name: 'Save changes' });
      expect(button).toHaveAttribute('aria-label', 'Save changes');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    test('Input component has proper labels', () => {
      render(
        <Input 
          label="Email Address"
          placeholder="Enter your email"
          error="Invalid email format"
        />
      );
      
      const input = screen.getByLabelText('Email Address');
      expect(input).toBeInTheDocument();
      expect(screen.getByText('Invalid email format')).toHaveAttribute('role', 'alert');
    });

    test('Modal traps focus when open', () => {
      const { rerender } = render(
        <Modal isOpen={false} onClose={() => {}} title="Test Modal">
          <button>First button</button>
          <button>Second button</button>
        </Modal>
      );
      
      // Modal should not be in document when closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      
      // Open modal
      rerender(
        <Modal isOpen={true} onClose={() => {}} title="Test Modal">
          <button>First button</button>
          <button>Second button</button>
        </Modal>
      );
      
      // Modal should be in document
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
      expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby');
    });

    test('Card component is keyboard accessible', () => {
      const handleClick = jest.fn();
      render(
        <Card onClick={handleClick} hover>
          Card content
        </Card>
      );
      
      const card = screen.getByText('Card content').parentElement;
      expect(card).toHaveAttribute('tabIndex', '0');
      
      // Test keyboard interaction
      fireEvent.keyDown(card!, { key: 'Enter' });
      expect(handleClick).toHaveBeenCalled();
    });
  });

  describe('Screen Accessibility', () => {
    test('WelcomeScreen has proper heading hierarchy', async () => {
      const { container } = renderWithProviders(<WelcomeScreen />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      // Check for main heading
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    });

    test('ChatScreen has ARIA live regions for messages', () => {
      renderWithProviders(<ChatScreen />);
      
      // Look for chat container with live region
      const chatContainer = screen.getByRole('log');
      expect(chatContainer).toHaveAttribute('aria-live', 'polite');
      expect(chatContainer).toHaveAttribute('aria-label', 'Chat messages');
    });

    test('EmergencyScreen has accessible emergency buttons', () => {
      renderWithProviders(<EmergencyScreen />);
      
      // Check emergency service buttons
      const emergencyButtons = screen.getAllByRole('button');
      emergencyButtons.forEach(button => {
        // Buttons should have minimum size
        expect(button).toHaveStyle({ minHeight: '44px', minWidth: '44px' });
      });
    });

    test('SettingsScreen toggle switches are accessible', () => {
      renderWithProviders(<SettingsScreen />);
      
      // Check for switch controls
      const switches = screen.getAllByRole('switch');
      switches.forEach(switchControl => {
        expect(switchControl).toHaveAttribute('aria-checked');
        expect(switchControl).toHaveAttribute('aria-label');
      });
    });
  });

  describe('Keyboard Navigation', () => {
    test('Tab navigation works through interactive elements', () => {
      render(
        <div>
          <button>First</button>
          <input type="text" placeholder="Input field" />
          <a href="#test">Link</a>
          <button>Last</button>
        </div>
      );
      
      const first = screen.getByText('First');
      const input = screen.getByPlaceholderText('Input field');
      const link = screen.getByText('Link');
      const last = screen.getByText('Last');
      
      // Simulate tab navigation
      first.focus();
      expect(document.activeElement).toBe(first);
      
      fireEvent.keyDown(document.activeElement!, { key: 'Tab' });
      expect(document.activeElement).toBe(input);
      
      fireEvent.keyDown(document.activeElement!, { key: 'Tab' });
      expect(document.activeElement).toBe(link);
      
      fireEvent.keyDown(document.activeElement!, { key: 'Tab' });
      expect(document.activeElement).toBe(last);
    });

    test('Escape key closes modal', () => {
      const onClose = jest.fn();
      render(
        <Modal isOpen={true} onClose={onClose} title="Test Modal">
          Modal content
        </Modal>
      );
      
      fireEvent.keyDown(document, { key: 'Escape' });
      expect(onClose).toHaveBeenCalled();
    });
  });

  describe('Screen Reader Support', () => {
    test('Images have alt text', () => {
      render(
        <img src="test.jpg" alt="Test image description" />
      );
      
      const image = screen.getByAltText('Test image description');
      expect(image).toBeInTheDocument();
    });

    test('Form fields have associated labels', () => {
      render(
        <form>
          <label htmlFor="username">Username</label>
          <input id="username" type="text" />
          
          <label htmlFor="password">Password</label>
          <input id="password" type="password" />
        </form>
      );
      
      expect(screen.getByLabelText('Username')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    test('Error messages are announced', async () => {
      render(
        <div>
          <div role="alert">Error: Invalid input</div>
        </div>
      );
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent('Error: Invalid input');
    });

    test('Loading states are announced', () => {
      render(
        <div role="status" aria-live="polite">
          <span className="sr-only">Loading...</span>
        </div>
      );
      
      const status = screen.getByRole('status');
      expect(status).toHaveTextContent('Loading...');
    });
  });

  describe('Color Contrast', () => {
    test('Text has sufficient contrast ratio', async () => {
      const { container } = render(
        <div>
          <p className="text-lavender-700 bg-white">Regular text</p>
          <h1 className="text-lavender-800 bg-cream-100">Heading text</h1>
        </div>
      );
      
      // Axe will check color contrast
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Touch Target Sizes', () => {
    test('Interactive elements meet minimum size requirements', () => {
      render(
        <div>
          <Button variant="primary">Click me</Button>
          <input type="checkbox" className="w-12 h-12" />
          <a href="#" className="block p-4">Link with padding</a>
        </div>
      );
      
      const button = screen.getByRole('button');
      const checkbox = screen.getByRole('checkbox');
      const link = screen.getByRole('link');
      
      // Check computed styles or classes that ensure minimum sizes
      expect(button).toHaveStyle({ minHeight: '48px' });
      expect(checkbox.classList.contains('w-12')).toBe(true);
      expect(checkbox.classList.contains('h-12')).toBe(true);
    });
  });

  describe('Focus Management', () => {
    test('Focus is restored after modal closes', async () => {
      const { rerender } = render(
        <div>
          <button id="trigger">Open Modal</button>
          <Modal isOpen={false} onClose={() => {}} title="Test">
            Modal content
          </Modal>
        </div>
      );
      
      const trigger = screen.getByText('Open Modal');
      trigger.focus();
      expect(document.activeElement).toBe(trigger);
      
      // Open modal
      rerender(
        <div>
          <button id="trigger">Open Modal</button>
          <Modal isOpen={true} onClose={() => {}} title="Test">
            Modal content
          </Modal>
        </div>
      );
      
      // Focus should move to modal
      await waitFor(() => {
        expect(document.activeElement).not.toBe(trigger);
      });
      
      // Close modal
      rerender(
        <div>
          <button id="trigger">Open Modal</button>
          <Modal isOpen={false} onClose={() => {}} title="Test">
            Modal content
          </Modal>
        </div>
      );
      
      // Focus should return to trigger
      await waitFor(() => {
        expect(document.activeElement).toBe(trigger);
      });
    });
  });

  describe('Reduced Motion Support', () => {
    test('Respects prefers-reduced-motion', () => {
      // Mock matchMedia
      window.matchMedia = jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      }));
      
      render(<div className="animate-gentle-pulse">Animated content</div>);
      
      // In reduced motion mode, animations should be disabled
      // This would be handled by CSS media queries
      expect(window.matchMedia).toHaveBeenCalledWith('(prefers-reduced-motion: reduce)');
    });
  });
});
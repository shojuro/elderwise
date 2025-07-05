import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

// Create a custom render function that includes providers
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
});

interface AllTheProvidersProps {
  children: React.ReactNode;
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Mock data generators
export const createMockUser = (overrides = {}) => ({
  id: 'test-user-123',
  name: 'Test User',
  email: 'test@example.com',
  role: 'elderly',
  createdAt: new Date().toISOString(),
  ...overrides,
});

export const createMockChatMessage = (overrides = {}) => ({
  id: 'msg-123',
  content: 'Test message',
  sender: 'user',
  timestamp: new Date().toISOString(),
  type: 'text',
  ...overrides,
});

export const createMockMemory = (overrides = {}) => ({
  id: 'mem-123',
  userId: 'test-user-123',
  content: 'Test memory content',
  type: 'event',
  tags: ['test'],
  timestamp: new Date().toISOString(),
  retention: 'active',
  ...overrides,
});

// Common test utilities
export const waitForLoadingToFinish = () => 
  waitFor(() => {
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });

export const expectErrorMessage = (message: string) => {
  expect(screen.getByRole('alert')).toHaveTextContent(message);
};

export const expectSuccessMessage = (message: string) => {
  expect(screen.getByText(message)).toHaveClass('text-sage-600');
};

// Mock API responses
export const mockApiResponse = (data: any, delay = 0) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ data }), delay);
  });
};

export const mockApiError = (message: string, status = 500, delay = 0) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject({ 
      response: { 
        status, 
        data: { detail: message } 
      } 
    }), delay);
  });
};

// Accessibility testing helpers
export const expectAccessibleName = (element: HTMLElement, name: string) => {
  expect(element).toHaveAccessibleName(name);
};

export const expectAccessibleDescription = (element: HTMLElement, description: string) => {
  expect(element).toHaveAccessibleDescription(description);
};

export const expectKeyboardNavigable = (element: HTMLElement) => {
  expect(element).toHaveAttribute('tabIndex');
  const tabIndex = element.getAttribute('tabIndex');
  expect(Number(tabIndex)).toBeGreaterThanOrEqual(0);
};
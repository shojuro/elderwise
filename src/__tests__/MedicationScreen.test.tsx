import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { Camera } from '@capacitor/camera';

import MedicationScreen from '../screens/main/MedicationScreen';
import * as api from '../services/api';
import * as cameraUtils from '../utils/camera';

// Mock modules
vi.mock('@capacitor/camera');
vi.mock('../services/api');
vi.mock('../utils/camera');

// Mock data
const mockMedication = {
  medication_id: '198440',
  name: 'Acetaminophen 500 mg',
  generic_name: 'acetaminophen',
  brand_names: ['Tylenol'],
  shape: 'oval',
  color: 'white',
  imprint: 'L484',
  dosage_forms: ['tablet'],
  strength: '500 mg',
  manufacturer: 'Kroger Company'
};

const mockMedicationDetails = {
  ...mockMedication,
  indications: ['Pain relief', 'Fever reduction'],
  contraindications: ['Severe liver disease'],
  side_effects: {
    common: ['Nausea', 'Stomach pain'],
    rare: ['Skin rash'],
    severe: ['Liver damage']
  },
  warnings: ['Do not exceed 4000mg per day'],
  drug_interactions: [
    {
      drug_name: 'Warfarin',
      severity: 'moderate',
      description: 'May increase bleeding risk',
      management: 'Monitor INR'
    }
  ],
  food_interactions: [],
  storage_instructions: 'Store at room temperature'
};

const mockUserMedication = {
  id: 'med_user_001',
  user_id: 'user123',
  medication_id: '198440',
  name: 'Acetaminophen 500 mg',
  dosage: '500mg',
  frequency: 'Every 6 hours as needed',
  purpose: 'Pain relief',
  active: true,
  created_at: new Date().toISOString()
};

describe('MedicationScreen', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementations
    (api.getUserMedications as any).mockResolvedValue([mockUserMedication]);
    (api.getMedicationDetails as any).mockResolvedValue(mockMedicationDetails);
    (cameraUtils.checkCameraPermissions as any).mockResolvedValue(true);
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <MedicationScreen />
      </BrowserRouter>
    );
  };

  describe('Component Rendering', () => {
    it('renders medication screen with all sections', async () => {
      renderComponent();

      expect(screen.getByText('My Medications')).toBeInTheDocument();
      expect(screen.getByText('Identify Medication')).toBeInTheDocument();
      expect(screen.getByText('Current Medications')).toBeInTheDocument();

      // Wait for medications to load
      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });
    });

    it('displays loading state while fetching medications', () => {
      (api.getUserMedications as any).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderComponent();

      expect(screen.getByText('Loading medications...')).toBeInTheDocument();
    });

    it('displays empty state when no medications', async () => {
      (api.getUserMedications as any).mockResolvedValue([]);

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('No medications added yet')).toBeInTheDocument();
      });
    });
  });

  describe('Camera Functionality', () => {
    it('opens camera when take photo button is clicked', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockResolvedValue({
        status: 'success',
        medications: [mockMedication],
        confidence: 0.9
      });

      renderComponent();

      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      expect(cameraUtils.checkCameraPermissions).toHaveBeenCalled();
      expect(Camera.getPhoto).toHaveBeenCalledWith({
        resultType: expect.anything(),
        source: expect.anything(),
        quality: 90
      });
    });

    it('handles camera permission denied', async () => {
      (cameraUtils.checkCameraPermissions as any).mockResolvedValue(false);

      renderComponent();

      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      await waitFor(() => {
        expect(screen.getByText(/camera permission required/i)).toBeInTheDocument();
      });
    });

    it('displays medication results after identification', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockResolvedValue({
        status: 'success',
        medications: [mockMedication],
        confidence: 0.9
      });

      renderComponent();

      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      await waitFor(() => {
        expect(screen.getByText('Medication Identified!')).toBeInTheDocument();
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
        expect(screen.getByText('L484')).toBeInTheDocument();
        expect(screen.getByText('90% confidence')).toBeInTheDocument();
      });
    });

    it('handles no medication found', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockRejectedValue({
        response: { status: 404 }
      });

      renderComponent();

      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      await waitFor(() => {
        expect(screen.getByText(/no medication found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Medication Details', () => {
    it('shows medication details when view details is clicked', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockResolvedValue({
        status: 'success',
        medications: [mockMedication],
        confidence: 0.9
      });

      renderComponent();

      // Take photo and identify medication
      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Medication Identified!')).toBeInTheDocument();
      });

      // Click view details
      const viewDetailsButton = screen.getByRole('button', { name: /view details/i });
      await user.click(viewDetailsButton);

      await waitFor(() => {
        expect(screen.getByText('Medication Details')).toBeInTheDocument();
        expect(screen.getByText(/pain relief/i)).toBeInTheDocument();
        expect(screen.getByText(/do not exceed 4000mg/i)).toBeInTheDocument();
      });
    });

    it('displays all medication detail sections', async () => {
      renderComponent();

      // Click on existing medication
      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });

      const medicationCard = screen.getByText('Acetaminophen 500 mg').closest('div');
      await user.click(medicationCard!);

      await waitFor(() => {
        // Check all sections are displayed
        expect(screen.getByText('Uses')).toBeInTheDocument();
        expect(screen.getByText('Warnings')).toBeInTheDocument();
        expect(screen.getByText('Side Effects')).toBeInTheDocument();
        expect(screen.getByText('Drug Interactions')).toBeInTheDocument();
        expect(screen.getByText('Storage')).toBeInTheDocument();
      });
    });
  });

  describe('Adding Medications', () => {
    it('adds medication to user list', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockResolvedValue({
        status: 'success',
        medications: [mockMedication],
        confidence: 0.9
      });
      (api.addUserMedication as any).mockResolvedValue({
        status: 'success',
        id: 'med_user_002'
      });

      renderComponent();

      // Take photo and identify medication
      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      await waitFor(() => {
        expect(screen.getByText('Medication Identified!')).toBeInTheDocument();
      });

      // Click add to my medications
      const addButton = screen.getByRole('button', { name: /add to my medications/i });
      await user.click(addButton);

      // Fill out the form
      await waitFor(() => {
        expect(screen.getByText('Add Medication')).toBeInTheDocument();
      });

      const dosageInput = screen.getByLabelText(/dosage/i);
      const frequencyInput = screen.getByLabelText(/frequency/i);
      const purposeInput = screen.getByLabelText(/purpose/i);

      await user.type(dosageInput, '500mg');
      await user.type(frequencyInput, 'Every 6 hours');
      await user.type(purposeInput, 'Headache relief');

      // Submit form
      const saveButton = screen.getByRole('button', { name: /save medication/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(api.addUserMedication).toHaveBeenCalledWith({
          user_id: expect.any(String),
          medication_id: '198440',
          name: 'Acetaminophen 500 mg',
          dosage: '500mg',
          frequency: 'Every 6 hours',
          purpose: 'Headache relief'
        });
      });

      expect(screen.getByText(/medication added successfully/i)).toBeInTheDocument();
    });
  });

  describe('Managing Medications', () => {
    it('updates medication information', async () => {
      (api.updateUserMedication as any).mockResolvedValue({
        status: 'success'
      });

      renderComponent();

      // Wait for medications to load
      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });

      // Click edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Update frequency
      const frequencyInput = screen.getByLabelText(/frequency/i);
      await user.clear(frequencyInput);
      await user.type(frequencyInput, 'Every 8 hours');

      // Save changes
      const saveButton = screen.getByRole('button', { name: /save changes/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(api.updateUserMedication).toHaveBeenCalledWith(
          'med_user_001',
          expect.objectContaining({
            frequency: 'Every 8 hours'
          })
        );
      });
    });

    it('deletes medication from user list', async () => {
      (api.deleteUserMedication as any).mockResolvedValue({
        status: 'success'
      });

      renderComponent();

      // Wait for medications to load
      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });

      // Click delete button
      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      // Confirm deletion
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /yes, delete/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(api.deleteUserMedication).toHaveBeenCalledWith('med_user_001');
      });
    });
  });

  describe('Drug Interactions', () => {
    it('checks for drug interactions', async () => {
      (api.getUserMedications as any).mockResolvedValue([
        mockUserMedication,
        {
          ...mockUserMedication,
          id: 'med_user_002',
          medication_id: '123456',
          name: 'Warfarin 5mg'
        }
      ]);

      (api.checkInteractions as any).mockResolvedValue({
        'Acetaminophen 500 mg + Warfarin 5mg': [
          {
            drug_name: 'Warfarin + Acetaminophen',
            severity: 'moderate',
            description: 'May increase bleeding risk',
            management: 'Monitor INR'
          }
        ]
      });

      renderComponent();

      // Wait for medications to load
      await waitFor(() => {
        expect(screen.getByText('Warfarin 5mg')).toBeInTheDocument();
      });

      // Click check interactions button
      const checkButton = screen.getByRole('button', { name: /check interactions/i });
      await user.click(checkButton);

      await waitFor(() => {
        expect(screen.getByText('Drug Interactions Found')).toBeInTheDocument();
        expect(screen.getByText(/may increase bleeding risk/i)).toBeInTheDocument();
        expect(screen.getByText('Moderate')).toBeInTheDocument();
      });
    });

    it('shows no interactions message when none found', async () => {
      (api.checkInteractions as any).mockResolvedValue({});

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });

      const checkButton = screen.getByRole('button', { name: /check interactions/i });
      await user.click(checkButton);

      await waitFor(() => {
        expect(screen.getByText(/no drug interactions found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error when medication loading fails', async () => {
      (api.getUserMedications as any).mockRejectedValue(new Error('Network error'));

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText(/error loading medications/i)).toBeInTheDocument();
      });
    });

    it('shows error when adding medication fails', async () => {
      const mockPhoto = { base64String: 'mock_base64_image' };
      (Camera.getPhoto as any).mockResolvedValue(mockPhoto);
      (api.identifyMedication as any).mockResolvedValue({
        status: 'success',
        medications: [mockMedication],
        confidence: 0.9
      });
      (api.addUserMedication as any).mockRejectedValue(new Error('Server error'));

      renderComponent();

      // Identify medication
      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      await waitFor(() => {
        expect(screen.getByText('Medication Identified!')).toBeInTheDocument();
      });

      // Try to add medication
      const addButton = screen.getByRole('button', { name: /add to my medications/i });
      await user.click(addButton);

      // Fill form and submit
      await waitFor(() => {
        expect(screen.getByText('Add Medication')).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /save medication/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/error adding medication/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for interactive elements', () => {
      renderComponent();

      expect(screen.getByRole('button', { name: /take photo/i })).toHaveAttribute(
        'aria-label'
      );
      expect(screen.getByRole('region', { name: /medication list/i })).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
      });

      // Tab to medication card
      await user.tab();
      await user.tab();

      // Press Enter to view details
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText('Medication Details')).toBeInTheDocument();
      });
    });

    it('announces changes to screen readers', async () => {
      renderComponent();

      const takePhotoButton = screen.getByRole('button', { name: /take photo/i });
      await user.click(takePhotoButton);

      // Check for live region updates
      await waitFor(() => {
        const liveRegion = screen.getByRole('status');
        expect(liveRegion).toHaveTextContent(/identifying medication/i);
      });
    });
  });
});
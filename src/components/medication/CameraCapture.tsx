import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, X, Image, HelpCircle, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';
import { cameraUtils, cameraInstructions, validateMedicationPhoto, PhotoResult } from '../../utils/camera';
import { hapticFeedback, isMobile } from '../../utils/capacitor';

interface CameraCaptureProps {
  onPhotoCapture: (photo: PhotoResult) => void;
  onCancel: () => void;
  isOpen: boolean;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({
  onPhotoCapture,
  onCancel,
  isOpen
}) => {
  const [showInstructions, setShowInstructions] = useState(true);
  const [capturedPhoto, setCapturedPhoto] = useState<PhotoResult | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTakePhoto = async () => {
    try {
      setError(null);
      setIsCapturing(true);
      
      const photo = await cameraUtils.takePhoto({
        quality: 90,
        saveToGallery: true
      });
      
      if (photo) {
        // Validate photo
        const validation = await validateMedicationPhoto(photo.base64Data);
        
        if (!validation.isValid) {
          setError(validation.issues[0]);
          setCapturedPhoto(null);
        } else {
          setCapturedPhoto(photo);
          setShowInstructions(false);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to take photo');
      await hapticFeedback.error();
    } finally {
      setIsCapturing(false);
    }
  };

  const handleSelectFromGallery = async () => {
    try {
      setError(null);
      setIsCapturing(true);
      
      const photo = await cameraUtils.selectFromGallery();
      
      if (photo) {
        const validation = await validateMedicationPhoto(photo.base64Data);
        
        if (!validation.isValid) {
          setError(validation.issues[0]);
          setCapturedPhoto(null);
        } else {
          setCapturedPhoto(photo);
          setShowInstructions(false);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to select photo');
      await hapticFeedback.error();
    } finally {
      setIsCapturing(false);
    }
  };

  const handleRetake = () => {
    setCapturedPhoto(null);
    setError(null);
    setShowInstructions(true);
  };

  const handleConfirm = () => {
    if (capturedPhoto) {
      onPhotoCapture(capturedPhoto);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title="Take Medication Photo"
      size="lg"
    >
      <AnimatePresence mode="wait">
        {showInstructions && !capturedPhoto ? (
          <motion.div
            key="instructions"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Instructions Header */}
            <div className="text-center">
              <div className="w-20 h-20 bg-lavender-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Camera size={40} className="text-white" />
              </div>
              <h2 className="text-elder-h2 mb-2">
                {cameraInstructions.medication.title}
              </h2>
              <p className="text-elder-body text-lavender-600">
                Follow these simple steps for best results
              </p>
            </div>

            {/* Step by Step Instructions */}
            <div className="bg-sage-50 rounded-elder p-6 space-y-4">
              <h3 className="text-elder-h3 text-sage-800 mb-3">Steps:</h3>
              {cameraInstructions.medication.steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3"
                >
                  <div className="w-8 h-8 bg-sage-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm font-bold">{index + 1}</span>
                  </div>
                  <p className="text-elder-body text-sage-700">{step}</p>
                </motion.div>
              ))}
            </div>

            {/* Tips */}
            <div className="bg-lavender-50 rounded-elder p-6">
              <h3 className="text-elder-h3 text-lavender-800 mb-3 flex items-center">
                <HelpCircle size={20} className="mr-2" />
                Helpful Tips
              </h3>
              <ul className="space-y-2">
                {cameraInstructions.medication.tips.map((tip, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle size={16} className="text-lavender-600 mr-2 mt-1 flex-shrink-0" />
                    <span className="text-elder-caption text-lavender-700">{tip}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button
                variant="primary"
                size="xl"
                fullWidth
                onClick={handleTakePhoto}
                disabled={isCapturing || !isMobile}
                icon={Camera}
              >
                {isCapturing ? 'Opening Camera...' : 'Take Photo'}
              </Button>
              
              <Button
                variant="secondary"
                size="lg"
                fullWidth
                onClick={handleSelectFromGallery}
                disabled={isCapturing || !isMobile}
                icon={Image}
              >
                Choose from Gallery
              </Button>
              
              <Button
                variant="ghost"
                size="lg"
                fullWidth
                onClick={onCancel}
              >
                Cancel
              </Button>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-coral-50 border border-coral-200 rounded-elder p-4"
              >
                <div className="flex items-start">
                  <AlertCircle className="text-coral-500 mr-3 flex-shrink-0" size={20} />
                  <p className="text-elder-body text-coral-700">{error}</p>
                </div>
              </motion.div>
            )}

            {/* Mobile Check */}
            {!isMobile && (
              <div className="bg-orange-50 border border-orange-200 rounded-elder p-4">
                <p className="text-elder-body text-orange-700 text-center">
                  Camera features are only available on mobile devices
                </p>
              </div>
            )}
          </motion.div>
        ) : capturedPhoto ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="space-y-6"
          >
            {/* Photo Preview */}
            <div className="text-center">
              <h2 className="text-elder-h2 mb-4">Review Your Photo</h2>
              <div className="relative inline-block">
                <img
                  src={`data:image/${capturedPhoto.format};base64,${capturedPhoto.base64Data}`}
                  alt="Captured medication"
                  className="max-w-full h-auto rounded-elder shadow-lg max-h-96"
                />
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, type: 'spring' }}
                  className="absolute -top-4 -right-4 w-12 h-12 bg-sage-500 rounded-full flex items-center justify-center"
                >
                  <CheckCircle className="text-white" size={24} />
                </motion.div>
              </div>
            </div>

            {/* Confirmation Message */}
            <div className="bg-sage-50 rounded-elder p-6 text-center">
              <p className="text-elder-body text-sage-700">
                Is this photo clear and shows the medication well?
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button
                variant="primary"
                size="xl"
                fullWidth
                onClick={handleConfirm}
                icon={CheckCircle}
              >
                Yes, Use This Photo
              </Button>
              
              <Button
                variant="secondary"
                size="lg"
                fullWidth
                onClick={handleRetake}
                icon={Camera}
              >
                Take Another Photo
              </Button>
              
              <Button
                variant="ghost"
                size="lg"
                fullWidth
                onClick={onCancel}
              >
                Cancel
              </Button>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </Modal>
  );
};
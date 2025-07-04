import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Camera,
  Pill,
  AlertTriangle,
  Info,
  Plus,
  Search,
  Clock,
  CheckCircle,
  XCircle,
  ChevronRight,
  FileText,
  Heart
} from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { CameraCapture } from '../../components/medication/CameraCapture';
import { useAppStore } from '../../store';
import { PhotoResult } from '../../utils/camera';
import { api } from '../../services/api';

interface IdentifiedMedication {
  id: string;
  name: string;
  genericName: string;
  strength: string;
  shape: string;
  color: string;
  imprint: string;
  confidence: number;
}

interface MedicationDetails {
  id: string;
  name: string;
  genericName: string;
  indications: string[];
  sideEffects: {
    common: string[];
    severe: string[];
  };
  interactions: {
    drugs: Array<{
      name: string;
      severity: string;
      description: string;
    }>;
    foods: Array<{
      item: string;
      severity: string;
      description: string;
    }>;
  };
  warnings: string[];
}

export const MedicationScreen: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAppStore();
  const [showCamera, setShowCamera] = useState(false);
  const [isIdentifying, setIsIdentifying] = useState(false);
  const [identifiedMeds, setIdentifiedMeds] = useState<IdentifiedMedication[]>([]);
  const [selectedMed, setSelectedMed] = useState<MedicationDetails | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePhotoCapture = async (photo: PhotoResult) => {
    setShowCamera(false);
    setIsIdentifying(true);
    setError(null);

    try {
      const response = await api.post('/medication/identify', {
        user_id: user?.id || 'anonymous',
        image_data: `data:image/${photo.format};base64,${photo.base64Data}`,
        save_to_profile: false
      });

      if (response.data.success && response.data.medications.length > 0) {
        setIdentifiedMeds(response.data.medications);
      } else {
        setError('Could not identify the medication. Please try again with a clearer photo.');
      }
    } catch (err) {
      setError('Unable to identify medication. Please try again.');
      console.error('Medication identification error:', err);
    } finally {
      setIsIdentifying(false);
    }
  };

  const handleSelectMedication = async (medication: IdentifiedMedication) => {
    try {
      const response = await api.get(`/medication/${medication.id}`);
      setSelectedMed(response.data);
      setShowDetails(true);
    } catch (err) {
      setError('Unable to load medication details.');
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 500,
        damping: 30
      }
    }
  };

  return (
    <ElderlyLayout title="Medication Identification">
      <motion.div
        className="min-h-screen pb-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div
          variants={itemVariants}
          className="text-center mb-8 pt-4"
        >
          <motion.div
            className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4"
            animate={{
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          >
            <Pill size={32} className="text-white" />
          </motion.div>

          <h1 className="text-elder-h1 mb-2">Medication Helper</h1>
          <p className="text-elder-body text-lavender-600">
            Take a photo to identify your medication
          </p>
        </motion.div>

        {/* Main Action */}
        {!isIdentifying && identifiedMeds.length === 0 && (
          <motion.div variants={itemVariants} className="px-4 mb-8">
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <div className="text-center py-8">
                <div className="w-24 h-24 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Camera size={48} className="text-white" />
                </div>
                <h2 className="text-elder-h2 mb-4">Identify Your Medication</h2>
                <p className="text-elder-body text-blue-700 mb-6 max-w-md mx-auto">
                  Take a clear photo of your pill or medication bottle to get detailed information
                </p>
                <Button
                  variant="primary"
                  size="xl"
                  onClick={() => setShowCamera(true)}
                  icon={Camera}
                >
                  Take Photo
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Loading State */}
        {isIdentifying && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="px-4"
          >
            <Card className="text-center py-12">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-16 h-16 border-4 border-lavender-500 border-t-transparent rounded-full mx-auto mb-4"
              />
              <h3 className="text-elder-h2 mb-2">Identifying Medication</h3>
              <p className="text-elder-body text-lavender-600">
                This may take a few moments...
              </p>
            </Card>
          </motion.div>
        )}

        {/* Identification Results */}
        {identifiedMeds.length > 0 && (
          <motion.div variants={itemVariants} className="px-4 mb-8">
            <h2 className="text-elder-h2 mb-4">Possible Matches</h2>
            <div className="space-y-4">
              {identifiedMeds.map((med, index) => (
                <motion.div
                  key={med.id}
                  variants={itemVariants}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    hover
                    onClick={() => handleSelectMedication(med)}
                    className="cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-500 rounded-elder flex items-center justify-center">
                          <Pill size={24} className="text-white" />
                        </div>
                        <div>
                          <h3 className="text-elder-h3">{med.name}</h3>
                          <p className="text-elder-body text-gray-600">
                            {med.genericName} • {med.strength}
                          </p>
                          <div className="flex items-center mt-1 space-x-4">
                            <span className="text-elder-caption">
                              Shape: {med.shape}
                            </span>
                            <span className="text-elder-caption">
                              Color: {med.color}
                            </span>
                            {med.imprint && (
                              <span className="text-elder-caption">
                                Imprint: {med.imprint}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-right">
                          <p className="text-elder-caption text-sage-600">
                            {Math.round(med.confidence * 100)}% match
                          </p>
                        </div>
                        <ChevronRight size={20} className="text-lavender-400" />
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>

            <motion.div variants={itemVariants} className="mt-6 space-y-3">
              <Button
                variant="secondary"
                size="lg"
                fullWidth
                onClick={() => setShowCamera(true)}
                icon={Camera}
              >
                Take Another Photo
              </Button>
              <Button
                variant="ghost"
                size="lg"
                fullWidth
                onClick={() => {
                  setIdentifiedMeds([]);
                  setError(null);
                }}
              >
                Start Over
              </Button>
            </motion.div>
          </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="px-4 mb-8"
          >
            <Card className="bg-coral-50 border-coral-200">
              <div className="flex items-start">
                <AlertTriangle className="text-coral-500 mr-3 flex-shrink-0" size={24} />
                <div>
                  <h3 className="text-elder-h3 text-coral-700 mb-2">
                    Unable to Identify
                  </h3>
                  <p className="text-elder-body text-coral-600">{error}</p>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Quick Links */}
        <motion.div variants={itemVariants} className="px-4">
          <h2 className="text-elder-h2 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card
              hover
              onClick={() => navigate('/health')}
              className="cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-sage-500 rounded-elder flex items-center justify-center">
                  <Clock size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="text-elder-h3">Medication Schedule</h3>
                  <p className="text-elder-caption">View your reminders</p>
                </div>
              </div>
            </Card>

            <Card
              hover
              onClick={() => navigate('/health')}
              className="cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-coral-500 rounded-elder flex items-center justify-center">
                  <Heart size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="text-elder-h3">Health Tracking</h3>
                  <p className="text-elder-caption">Monitor your health</p>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      </motion.div>

      {/* Camera Modal */}
      <CameraCapture
        isOpen={showCamera}
        onPhotoCapture={handlePhotoCapture}
        onCancel={() => setShowCamera(false)}
      />

      {/* Medication Details Modal */}
      {selectedMed && (
        <Modal
          isOpen={showDetails}
          onClose={() => {
            setShowDetails(false);
            setSelectedMed(null);
          }}
          title={selectedMed.name}
          size="lg"
        >
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Pill size={32} className="text-white" />
              </div>
              <h2 className="text-elder-h2">{selectedMed.name}</h2>
              <p className="text-elder-body text-gray-600">
                {selectedMed.genericName}
              </p>
            </div>

            {/* Uses */}
            <div className="bg-sage-50 rounded-elder p-6">
              <h3 className="text-elder-h3 text-sage-800 mb-3 flex items-center">
                <Info size={20} className="mr-2" />
                What it's used for
              </h3>
              <ul className="space-y-2">
                {selectedMed.indications.map((indication, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle size={16} className="text-sage-600 mr-2 mt-1 flex-shrink-0" />
                    <span className="text-elder-body text-sage-700">{indication}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Warnings */}
            {selectedMed.warnings.length > 0 && (
              <div className="bg-orange-50 rounded-elder p-6">
                <h3 className="text-elder-h3 text-orange-800 mb-3 flex items-center">
                  <AlertTriangle size={20} className="mr-2" />
                  Important Warnings
                </h3>
                <ul className="space-y-2">
                  {selectedMed.warnings.map((warning, index) => (
                    <li key={index} className="text-elder-body text-orange-700">
                      • {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Side Effects */}
            <div>
              <h3 className="text-elder-h3 mb-3">Side Effects</h3>
              
              {selectedMed.sideEffects.common.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-elder-body font-medium mb-2">Common:</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedMed.sideEffects.common.map((effect, index) => (
                      <span
                        key={index}
                        className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                      >
                        {effect}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedMed.sideEffects.severe.length > 0 && (
                <div className="bg-coral-50 rounded-elder p-4">
                  <h4 className="text-elder-body font-medium text-coral-700 mb-2">
                    Severe (seek medical help):
                  </h4>
                  <ul className="space-y-1">
                    {selectedMed.sideEffects.severe.map((effect, index) => (
                      <li key={index} className="text-elder-caption text-coral-600">
                        • {effect}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Interactions */}
            {(selectedMed.interactions.drugs.length > 0 ||
              selectedMed.interactions.foods.length > 0) && (
              <div>
                <h3 className="text-elder-h3 mb-3">Interactions</h3>
                
                {selectedMed.interactions.drugs.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-elder-body font-medium mb-2">Drug Interactions:</h4>
                    {selectedMed.interactions.drugs.map((interaction, index) => (
                      <div
                        key={index}
                        className={`mb-2 p-3 rounded-elder ${
                          interaction.severity === 'major'
                            ? 'bg-coral-50 border border-coral-200'
                            : 'bg-orange-50 border border-orange-200'
                        }`}
                      >
                        <p className="font-medium text-sm">{interaction.name}</p>
                        <p className="text-elder-caption mt-1">{interaction.description}</p>
                      </div>
                    ))}
                  </div>
                )}

                {selectedMed.interactions.foods.length > 0 && (
                  <div>
                    <h4 className="text-elder-body font-medium mb-2">Food Interactions:</h4>
                    {selectedMed.interactions.foods.map((interaction, index) => (
                      <div key={index} className="flex items-start mb-2">
                        <AlertTriangle
                          size={16}
                          className={`mr-2 mt-1 flex-shrink-0 ${
                            interaction.severity === 'major'
                              ? 'text-coral-500'
                              : 'text-orange-500'
                          }`}
                        />
                        <div>
                          <p className="font-medium text-sm">{interaction.item}</p>
                          <p className="text-elder-caption">{interaction.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="space-y-3">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={() => {
                  // Add to user's medications
                  setShowDetails(false);
                }}
                icon={Plus}
              >
                Add to My Medications
              </Button>
              
              <Button
                variant="ghost"
                size="lg"
                fullWidth
                onClick={() => setShowDetails(false)}
              >
                Close
              </Button>
            </div>

            {/* Disclaimer */}
            <p className="text-elder-caption text-center text-gray-500">
              Always consult your healthcare provider or pharmacist for medical advice
            </p>
          </div>
        </Modal>
      )}
    </ElderlyLayout>
  );
};
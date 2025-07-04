import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowRight, ArrowLeft, Check, Plus, X } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { Card } from '../../components/common/Card';
import { AuthLayout } from '../../components/common/Layout';
import { useAppStore } from '../../store';
import { ContactForm } from '../../types';
import { apiService } from '../../services/api';

const SETUP_STEPS = [
  { id: 'personal', title: 'Tell us about yourself', subtitle: 'This helps ElderWise provide better support' },
  { id: 'health', title: 'Health information', subtitle: 'Optional: Share any conditions we should know about' },
  { id: 'interests', title: 'Your interests', subtitle: 'What do you enjoy talking about?' },
  { id: 'emergency', title: 'Emergency contacts', subtitle: 'Who should we contact if needed?' },
  { id: 'complete', title: 'All set!', subtitle: 'ElderWise is ready to be your companion' }
];

const COMMON_CONDITIONS = [
  'Diabetes', 'Hypertension', 'Arthritis', 'Heart Disease', 
  'Osteoporosis', 'COPD', 'Depression', 'Anxiety'
];

const COMMON_INTERESTS = [
  'Gardening', 'Cooking', 'Reading', 'Music', 'Movies', 'Travel',
  'Family', 'Pets', 'Sports', 'Crafts', 'History', 'Nature'
];

export const SetupScreen: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<ContactForm>({
    defaultValues: {
      name: '',
      age: 70,
      conditions: [],
      interests: [],
      emergencyContacts: []
    }
  });

  const watchedValues = watch();

  const nextStep = () => {
    if (currentStep < SETUP_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const toggleArrayItem = (array: string[], item: string, field: 'conditions' | 'interests') => {
    const newArray = array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
    setValue(field, newArray);
  };

  const addEmergencyContact = () => {
    const contacts = watchedValues.emergencyContacts || [];
    setValue('emergencyContacts', [
      ...contacts,
      { name: '', relationship: '', phone: '', isPrimary: contacts.length === 0 }
    ]);
  };

  const removeEmergencyContact = (index: number) => {
    const contacts = watchedValues.emergencyContacts || [];
    setValue('emergencyContacts', contacts.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: ContactForm) => {
    setIsLoading(true);
    
    try {
      // Generate a unique user ID
      const userId = 'user_' + Date.now();
      
      // Create user via API
      await apiService.createUser({
        user_id: userId,
        name: data.name,
        age: data.age || 70,
        conditions: data.conditions || [],
        interests: data.interests || []
      });
      
      // Create user object for local state
      const user = {
        id: userId,
        name: data.name,
        age: data.age,
        conditions: data.conditions,
        interests: data.interests,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        role: 'elderly' as const,
        emergencyContacts: data.emergencyContacts.map((contact, index) => ({
          ...contact,
          id: 'contact_' + index
        }))
      };

      setUser(user);
      setAuthenticated(true);
      
      nextStep(); // Go to completion step
      
      // Navigate to main app after showing completion
      setTimeout(() => {
        navigate('/chat');
      }, 3000);
      
    } catch (error) {
      console.error('Setup failed:', error);
      alert('Setup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const stepVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 }
  };

  const renderStep = () => {
    const step = SETUP_STEPS[currentStep];

    switch (step.id) {
      case 'personal':
        return (
          <div className="space-y-6">
            <Input
              label="What's your name?"
              placeholder="Enter your first name"
              {...register('name', { required: 'Name is required' })}
              error={errors.name?.message}
              fullWidth
            />
            
            <div>
              <label className="block text-elder-h3 mb-2">
                How old are you?
              </label>
              <input
                type="range"
                min="50"
                max="100"
                {...register('age', { required: true })}
                className="w-full h-3 bg-lavender-200 rounded-elder appearance-none cursor-pointer"
              />
              <div className="flex justify-between mt-2">
                <span className="text-elder-caption">50</span>
                <span className="text-elder-h3 text-lavender-800">{watchedValues.age}</span>
                <span className="text-elder-caption">100</span>
              </div>
            </div>
          </div>
        );

      case 'health':
        return (
          <div className="space-y-6">
            <p className="text-elder-body text-lavender-600">
              Sharing health information helps ElderWise provide better support. This is completely optional.
            </p>
            
            <div>
              <h3 className="text-elder-h3 mb-4">Common conditions (select any that apply):</h3>
              <div className="grid grid-cols-2 gap-3">
                {COMMON_CONDITIONS.map((condition) => (
                  <Button
                    key={condition}
                    variant={watchedValues.conditions?.includes(condition) ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => toggleArrayItem(watchedValues.conditions || [], condition, 'conditions')}
                    className="text-left justify-start"
                  >
                    {condition}
                  </Button>
                ))}
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const custom = prompt('Enter a condition not listed:');
                if (custom) {
                  toggleArrayItem(watchedValues.conditions || [], custom, 'conditions');
                }
              }}
              icon={Plus}
            >
              Add other condition
            </Button>
          </div>
        );

      case 'interests':
        return (
          <div className="space-y-6">
            <p className="text-elder-body text-lavender-600">
              Tell us what you enjoy so we can have better conversations!
            </p>
            
            <div>
              <h3 className="text-elder-h3 mb-4">What do you like to talk about?</h3>
              <div className="grid grid-cols-2 gap-3">
                {COMMON_INTERESTS.map((interest) => (
                  <Button
                    key={interest}
                    variant={watchedValues.interests?.includes(interest) ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => toggleArrayItem(watchedValues.interests || [], interest, 'interests')}
                    className="text-left justify-start"
                  >
                    {interest}
                  </Button>
                ))}
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const custom = prompt('Enter an interest not listed:');
                if (custom) {
                  toggleArrayItem(watchedValues.interests || [], custom, 'interests');
                }
              }}
              icon={Plus}
            >
              Add other interest
            </Button>
          </div>
        );

      case 'emergency':
        return (
          <div className="space-y-6">
            <p className="text-elder-body text-lavender-600">
              Add contacts who should be notified in case of emergency. You can add more later.
            </p>
            
            <div className="space-y-4">
              {(watchedValues.emergencyContacts || []).map((contact, index) => (
                <Card key={index} className="p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-elder-h3">
                      Contact {index + 1} {contact.isPrimary && '(Primary)'}
                    </h4>
                    {watchedValues.emergencyContacts && watchedValues.emergencyContacts.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeEmergencyContact(index)}
                        icon={X}
                        ariaLabel="Remove contact"
                      />
                    )}
                  </div>
                  
                  <div className="space-y-3">
                    <Input
                      placeholder="Name"
                      {...register(`emergencyContacts.${index}.name`, { required: 'Name is required' })}
                      fullWidth
                    />
                    <Input
                      placeholder="Relationship (e.g., Daughter, Son)"
                      {...register(`emergencyContacts.${index}.relationship`)}
                      fullWidth
                    />
                    <Input
                      placeholder="Phone number"
                      type="tel"
                      {...register(`emergencyContacts.${index}.phone`, { required: 'Phone is required' })}
                      fullWidth
                    />
                  </div>
                </Card>
              ))}
            </div>

            <Button
              variant="secondary"
              onClick={addEmergencyContact}
              icon={Plus}
              fullWidth
            >
              Add Emergency Contact
            </Button>
          </div>
        );

      case 'complete':
        return (
          <motion.div
            className="text-center space-y-6"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <motion.div
              className="w-24 h-24 bg-sage-500 rounded-full flex items-center justify-center mx-auto mb-6"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 500, damping: 20, delay: 0.3 }}
            >
              <Check size={40} className="text-white" />
            </motion.div>
            
            <h2 className="text-elder-h1">Welcome aboard, {watchedValues.name}!</h2>
            
            <p className="text-elder-body text-lavender-600">
              ElderWise is now ready to be your caring companion. Let's start our first conversation!
            </p>

            <motion.div
              className="loading-dots justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              <div></div>
              <div></div>
              <div></div>
            </motion.div>
          </motion.div>
        );

      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (SETUP_STEPS[currentStep].id) {
      case 'personal':
        return watchedValues.name && watchedValues.name.trim().length > 0;
      case 'emergency':
        return (watchedValues.emergencyContacts || []).length > 0 &&
               watchedValues.emergencyContacts?.[0]?.name &&
               watchedValues.emergencyContacts?.[0]?.phone;
      default:
        return true;
    }
  };

  return (
    <AuthLayout>
      <div className="w-full max-w-2xl mx-auto">
        {/* Progress indicator */}
        {currentStep < SETUP_STEPS.length - 1 && (
          <div className="mb-8">
            <div className="flex justify-between mb-4">
              {SETUP_STEPS.slice(0, -1).map((_, index) => (
                <div
                  key={index}
                  className={`w-4 h-4 rounded-full ${
                    index <= currentStep ? 'bg-lavender-500' : 'bg-lavender-200'
                  }`}
                />
              ))}
            </div>
            <div className="h-2 bg-lavender-200 rounded-full">
              <motion.div
                className="h-full bg-lavender-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((currentStep + 1) / (SETUP_STEPS.length - 1)) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}

        {/* Step content */}
        <Card className="mb-8">
          <div className="text-center mb-8">
            <h1 className="text-elder-h1 mb-2">
              {SETUP_STEPS[currentStep].title}
            </h1>
            <p className="text-elder-body text-lavender-600">
              {SETUP_STEPS[currentStep].subtitle}
            </p>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              variants={stepVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={{ duration: 0.3 }}
            >
              {renderStep()}
            </motion.div>
          </AnimatePresence>
        </Card>

        {/* Navigation buttons */}
        {currentStep < SETUP_STEPS.length - 1 && (
          <div className="flex justify-between">
            <Button
              variant="ghost"
              onClick={prevStep}
              disabled={currentStep === 0}
              icon={ArrowLeft}
              iconPosition="left"
            >
              Back
            </Button>

            <Button
              onClick={currentStep === SETUP_STEPS.length - 2 ? handleSubmit(onSubmit) : nextStep}
              disabled={!canProceed() || isLoading}
              loading={isLoading}
              icon={ArrowRight}
              iconPosition="right"
            >
              {currentStep === SETUP_STEPS.length - 2 ? 'Complete Setup' : 'Next'}
            </Button>
          </div>
        )}
      </div>
    </AuthLayout>
  );
};
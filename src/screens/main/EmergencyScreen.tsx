import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Phone, 
  MessageCircle, 
  MapPin, 
  Heart, 
  AlertTriangle,
  Shield,
  Clock,
  User,
  Info
} from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';

// Mock emergency contacts - replace with actual data
const emergencyContacts = [
  {
    id: '1',
    name: 'Sarah Johnson',
    relationship: 'Daughter',
    phone: '(555) 123-4567',
    isPrimary: true,
    isAvailable: true
  },
  {
    id: '2',
    name: 'Dr. Smith',
    relationship: 'Family Doctor',
    phone: '(555) 987-6543',
    isPrimary: false,
    isAvailable: true
  },
  {
    id: '3',
    name: 'Mike Johnson',
    relationship: 'Son',
    phone: '(555) 555-0123',
    isPrimary: false,
    isAvailable: false
  }
];

const emergencyServices = [
  {
    id: 'emergency',
    name: 'Emergency Services',
    number: '911',
    description: 'Police, Fire, Medical Emergency',
    icon: AlertTriangle,
    color: 'coral',
    priority: 1
  },
  {
    id: 'poison',
    name: 'Poison Control',
    number: '1-800-222-1222',
    description: 'Poison Control Center',
    icon: Shield,
    color: 'orange',
    priority: 2
  },
  {
    id: 'nurse',
    name: 'Nurse Hotline',
    number: '1-800-NURSE-LINE',
    description: '24/7 Medical Advice',
    icon: Heart,
    color: 'sage',
    priority: 3
  }
];

export const EmergencyScreen: React.FC = () => {
  const [confirmCall, setConfirmCall] = useState<string | null>(null);
  const [isLocationSharing, setIsLocationSharing] = useState(false);
  const [lastLocationUpdate, setLastLocationUpdate] = useState<Date | null>(null);

  const handleEmergencyCall = (number: string, name: string) => {
    if (number === '911') {
      // For 911, show immediate confirmation
      setConfirmCall(`${name}|${number}`);
    } else {
      // For other numbers, call directly
      window.location.href = `tel:${number}`;
    }
  };

  const confirmEmergencyCall = () => {
    if (confirmCall) {
      const [name, number] = confirmCall.split('|');
      window.location.href = `tel:${number}`;
      setConfirmCall(null);
    }
  };

  const shareLocation = async () => {
    setIsLocationSharing(true);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLastLocationUpdate(new Date());
          setIsLocationSharing(false);
          // Here you would send location to emergency contacts
          console.log('Location shared:', position.coords);
        },
        (error) => {
          console.error('Location error:', error);
          setIsLocationSharing(false);
          alert('Unable to get location. Please check permissions.');
        }
      );
    } else {
      alert('Location sharing not supported');
      setIsLocationSharing(false);
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
    <ElderlyLayout title="Emergency Help">
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
            className="w-16 h-16 bg-coral-500 rounded-full flex items-center justify-center mx-auto mb-4"
            animate={{ 
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            <Shield size={28} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-2">Emergency Help</h1>
          <p className="text-elder-body text-lavender-600">
            Quick access to emergency services and your contacts
          </p>
        </motion.div>

        {/* Emergency Services */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Emergency Services</h2>
          
          <div className="space-y-3">
            {emergencyServices.map((service) => (
              <motion.div
                key={service.id}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => handleEmergencyCall(service.number, service.name)}
                  className="cursor-pointer border-2 hover:border-coral-300 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`
                        w-14 h-14 rounded-elder flex items-center justify-center
                        ${service.color === 'coral' ? 'bg-coral-500' : ''}
                        ${service.color === 'orange' ? 'bg-orange-500' : ''}
                        ${service.color === 'sage' ? 'bg-sage-500' : ''}
                      `}>
                        <service.icon size={28} className="text-white" />
                      </div>
                      
                      <div>
                        <h3 className="text-elder-h3">{service.name}</h3>
                        <p className="text-elder-body font-bold text-2xl">{service.number}</p>
                        <p className="text-elder-caption">{service.description}</p>
                      </div>
                    </div>
                    
                    <Phone size={24} className="text-lavender-400" />
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Personal Contacts */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Personal Contacts</h2>
          
          <div className="space-y-3">
            {emergencyContacts.map((contact) => (
              <motion.div
                key={contact.id}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => window.location.href = `tel:${contact.phone}`}
                  className={`
                    cursor-pointer transition-colors
                    ${contact.isPrimary ? 'border-2 border-sage-300 bg-sage-50' : ''}
                    ${!contact.isAvailable ? 'opacity-60' : 'hover:border-lavender-300'}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`
                        w-12 h-12 rounded-elder flex items-center justify-center
                        ${contact.isPrimary ? 'bg-sage-500' : 'bg-lavender-500'}
                      `}>
                        <User size={24} className="text-white" />
                      </div>
                      
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-elder-h3">{contact.name}</h3>
                          {contact.isPrimary && (
                            <span className="px-2 py-1 bg-sage-100 text-sage-700 text-xs rounded-full">
                              Primary
                            </span>
                          )}
                        </div>
                        <p className="text-elder-body">{contact.relationship}</p>
                        <p className="text-elder-caption">{contact.phone}</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end space-y-1">
                      <Phone size={24} className="text-lavender-400" />
                      <div className={`w-2 h-2 rounded-full ${
                        contact.isAvailable ? 'bg-sage-500' : 'bg-gray-400'
                      }`} />
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Quick Actions</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card className="cursor-pointer hover:border-lavender-300 transition-colors">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500 rounded-elder flex items-center justify-center mx-auto mb-3">
                  <MessageCircle size={24} className="text-white" />
                </div>
                <h3 className="text-elder-h3 mb-2">Send Alert Message</h3>
                <p className="text-elder-caption">
                  Send "I need help" message to all contacts
                </p>
              </div>
            </Card>

            <Card 
              onClick={shareLocation}
              className="cursor-pointer hover:border-lavender-300 transition-colors"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-500 rounded-elder flex items-center justify-center mx-auto mb-3">
                  {isLocationSharing ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                      <Clock size={24} className="text-white" />
                    </motion.div>
                  ) : (
                    <MapPin size={24} className="text-white" />
                  )}
                </div>
                <h3 className="text-elder-h3 mb-2">Share Location</h3>
                <p className="text-elder-caption">
                  {isLocationSharing ? 'Sharing location...' : 'Send your location to contacts'}
                </p>
                {lastLocationUpdate && (
                  <p className="text-xs text-sage-600 mt-1">
                    Last shared: {lastLocationUpdate.toLocaleTimeString()}
                  </p>
                )}
              </div>
            </Card>
          </div>
        </motion.div>

        {/* Safety Information */}
        <motion.div variants={itemVariants} className="px-4">
          <Card className="bg-blue-50 border-blue-200">
            <div className="flex items-start space-x-3">
              <Info size={24} className="text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-elder-h3 text-blue-800 mb-2">Safety Tips</h3>
                <ul className="text-elder-body text-blue-700 space-y-1">
                  <li>• Stay calm in emergency situations</li>
                  <li>• Have your address ready when calling for help</li>
                  <li>• Keep this phone charged and nearby</li>
                  <li>• Test emergency contacts regularly</li>
                </ul>
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>

      {/* Emergency Confirmation Modal */}
      <Modal
        isOpen={!!confirmCall}
        onClose={() => setConfirmCall(null)}
        title="Confirm Emergency Call"
      >
        <div className="text-center space-y-6">
          <div className="w-16 h-16 bg-coral-500 rounded-full flex items-center justify-center mx-auto">
            <AlertTriangle size={32} className="text-white" />
          </div>
          
          <div>
            <h3 className="text-elder-h2 mb-2">Call Emergency Services?</h3>
            <p className="text-elder-body text-lavender-600">
              You are about to call <strong>911</strong> for emergency assistance.
            </p>
          </div>

          <div className="space-y-3">
            <Button
              variant="emergency"
              size="xl"
              fullWidth
              onClick={confirmEmergencyCall}
              icon={Phone}
            >
              Yes, Call 911 Now
            </Button>
            
            <Button
              variant="ghost"
              size="lg"
              fullWidth
              onClick={() => setConfirmCall(null)}
            >
              Cancel
            </Button>
          </div>

          <p className="text-elder-caption text-gray-600">
            Only call 911 for genuine emergencies requiring immediate assistance.
          </p>
        </div>
      </Modal>
    </ElderlyLayout>
  );
};
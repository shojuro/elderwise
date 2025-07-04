import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Heart, 
  Activity, 
  Calendar, 
  TrendingUp, 
  TrendingDown,
  AlertCircle,
  Plus,
  Pill,
  Clock,
  Target,
  Award,
  CheckCircle2,
  Camera
} from 'lucide-react';
import { format, startOfWeek, addDays, isSameDay } from 'date-fns';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { useNavigate } from 'react-router-dom';

interface HealthMetric {
  id: string;
  type: 'blood_pressure' | 'heart_rate' | 'weight' | 'medication' | 'mood';
  value: string;
  unit: string;
  timestamp: Date;
  note?: string;
}

interface MedicationReminder {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  nextDose: Date;
  taken: boolean;
}

// Mock data
const mockHealthMetrics: HealthMetric[] = [
  {
    id: '1',
    type: 'blood_pressure',
    value: '120/80',
    unit: 'mmHg',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    note: 'Feeling good today'
  },
  {
    id: '2',
    type: 'heart_rate',
    value: '72',
    unit: 'bpm',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000)
  },
  {
    id: '3',
    type: 'weight',
    value: '165',
    unit: 'lbs',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000)
  }
];

const mockMedications: MedicationReminder[] = [
  {
    id: '1',
    name: 'Lisinopril',
    dosage: '10mg',
    frequency: 'Once daily',
    nextDose: new Date(Date.now() + 2 * 60 * 60 * 1000),
    taken: false
  },
  {
    id: '2',
    name: 'Metformin',
    dosage: '500mg',
    frequency: 'Twice daily',
    nextDose: new Date(Date.now() + 4 * 60 * 60 * 1000),
    taken: true
  }
];

export const HealthScreen: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newMetricValue, setNewMetricValue] = useState('');
  const [selectedWeek, setSelectedWeek] = useState(new Date());

  const getMetricIcon = (type: string) => {
    switch (type) {
      case 'blood_pressure': return Heart;
      case 'heart_rate': return Activity;
      case 'weight': return TrendingUp;
      case 'medication': return Pill;
      case 'mood': return CheckCircle2;
      default: return Heart;
    }
  };

  const getMetricColor = (type: string) => {
    switch (type) {
      case 'blood_pressure': return 'coral';
      case 'heart_rate': return 'sage';
      case 'weight': return 'purple';
      case 'medication': return 'blue';
      case 'mood': return 'orange';
      default: return 'lavender';
    }
  };

  const markMedicationTaken = (id: string) => {
    // In a real app, this would update the backend
    console.log('Marking medication as taken:', id);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1
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

  const weekDays = Array.from({ length: 7 }, (_, i) => 
    addDays(startOfWeek(selectedWeek), i)
  );

  return (
    <ElderlyLayout title="Health Tracking">
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
            className="w-16 h-16 bg-sage-500 rounded-full flex items-center justify-center mx-auto mb-4"
            animate={{ 
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            <Heart size={28} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-2">Health Tracking</h1>
          <p className="text-elder-body text-lavender-600">
            Monitor your health metrics and medications
          </p>
        </motion.div>

        {/* Medication Reminders */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-elder-h2">Medication Reminders</h2>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                icon={Camera}
                onClick={() => navigate('/medication')}
              >
                Identify
              </Button>
              <Button
                variant="ghost"
                size="sm"
                icon={Plus}
                onClick={() => setShowAddModal(true)}
              >
                Add
              </Button>
            </div>
          </div>
          
          <div className="space-y-3">
            {mockMedications.map((medication) => (
              <motion.div
                key={medication.id}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card className={`
                  ${medication.taken ? 'bg-sage-50 border-sage-200' : 'bg-orange-50 border-orange-200'}
                  ${!medication.taken ? 'border-l-4 border-l-orange-500' : ''}
                `}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`
                        w-12 h-12 rounded-elder flex items-center justify-center
                        ${medication.taken ? 'bg-sage-500' : 'bg-orange-500'}
                      `}>
                        {medication.taken ? (
                          <CheckCircle2 size={24} className="text-white" />
                        ) : (
                          <Pill size={24} className="text-white" />
                        )}
                      </div>
                      
                      <div>
                        <h3 className="text-elder-h3">{medication.name}</h3>
                        <p className="text-elder-body">{medication.dosage}</p>
                        <p className="text-elder-caption flex items-center">
                          <Clock size={14} className="mr-1" />
                          Next dose: {format(medication.nextDose, 'h:mm a')}
                        </p>
                      </div>
                    </div>
                    
                    {!medication.taken && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => markMedicationTaken(medication.id)}
                      >
                        Mark Taken
                      </Button>
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Weekly Overview */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">This Week</h2>
          
          <div className="grid grid-cols-7 gap-2">
            {weekDays.map((day) => (
              <div
                key={day.toISOString()}
                className={`
                  text-center p-3 rounded-elder border-2 transition-colors
                  ${isSameDay(day, new Date()) ? 'bg-sage-500 border-sage-500 text-white' : 'bg-white border-lavender-200'}
                `}
              >
                <div className="text-xs font-medium">
                  {format(day, 'EEE')}
                </div>
                <div className="text-lg font-bold">
                  {format(day, 'd')}
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Recent Metrics */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-elder-h2">Recent Measurements</h2>
            <Button
              variant="ghost"
              size="sm"
              icon={Plus}
              onClick={() => setShowAddModal(true)}
            >
              Add
            </Button>
          </div>
          
          <div className="space-y-3">
            {mockHealthMetrics.map((metric) => {
              const Icon = getMetricIcon(metric.type);
              const color = getMetricColor(metric.type);
              
              return (
                <motion.div
                  key={metric.id}
                  variants={itemVariants}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    hover
                    onClick={() => setSelectedMetric(metric.id)}
                    className="cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`
                          w-12 h-12 rounded-elder flex items-center justify-center
                          ${color === 'coral' ? 'bg-coral-500' : ''}
                          ${color === 'sage' ? 'bg-sage-500' : ''}
                          ${color === 'purple' ? 'bg-purple-500' : ''}
                          ${color === 'blue' ? 'bg-blue-500' : ''}
                          ${color === 'orange' ? 'bg-orange-500' : ''}
                          ${color === 'lavender' ? 'bg-lavender-500' : ''}
                        `}>
                          <Icon size={24} className="text-white" />
                        </div>
                        
                        <div>
                          <h3 className="text-elder-h3 capitalize">
                            {metric.type.replace('_', ' ')}
                          </h3>
                          <p className="text-elder-body font-bold">
                            {metric.value} {metric.unit}
                          </p>
                          <p className="text-elder-caption">
                            {format(metric.timestamp, 'MMM d, h:mm a')}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <TrendingUp size={20} className="text-sage-500" />
                        <span className="text-elder-caption">Normal</span>
                      </div>
                    </div>
                    
                    {metric.note && (
                      <div className="mt-3 pt-3 border-t border-lavender-100">
                        <p className="text-elder-caption italic">
                          "{metric.note}"
                        </p>
                      </div>
                    )}
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Health Goals */}
        <motion.div variants={itemVariants} className="px-4">
          <h2 className="text-elder-h2 mb-4">Health Goals</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card className="bg-gradient-to-br from-sage-50 to-sage-100 border-sage-200">
              <div className="text-center">
                <div className="w-12 h-12 bg-sage-500 rounded-elder flex items-center justify-center mx-auto mb-3">
                  <Target size={24} className="text-white" />
                </div>
                <h3 className="text-elder-h3 mb-2">Daily Steps</h3>
                <p className="text-elder-body font-bold">2,847 / 5,000</p>
                <div className="w-full bg-sage-200 rounded-full h-2 mt-2">
                  <div className="bg-sage-500 h-2 rounded-full" style={{ width: '57%' }}></div>
                </div>
              </div>
            </Card>

            <Card className="bg-gradient-to-br from-coral-50 to-coral-100 border-coral-200">
              <div className="text-center">
                <div className="w-12 h-12 bg-coral-500 rounded-elder flex items-center justify-center mx-auto mb-3">
                  <Award size={24} className="text-white" />
                </div>
                <h3 className="text-elder-h3 mb-2">Medication Streak</h3>
                <p className="text-elder-body font-bold">12 days</p>
                <p className="text-elder-caption text-coral-600">
                  Keep up the great work!
                </p>
              </div>
            </Card>
          </div>
        </motion.div>
      </motion.div>

      {/* Add Metric Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setNewMetricValue('');
        }}
        title="Add Health Metric"
      >
        <div className="space-y-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-sage-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Plus size={32} className="text-white" />
            </div>
            <h3 className="text-elder-h2 mb-2">Record New Measurement</h3>
            <p className="text-elder-body text-lavender-600">
              Add a new health metric to track your progress
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-elder-body font-medium mb-2">
                Metric Type
              </label>
              <select className="w-full p-4 text-elder-body border-2 border-lavender-200 rounded-elder">
                <option value="blood_pressure">Blood Pressure</option>
                <option value="heart_rate">Heart Rate</option>
                <option value="weight">Weight</option>
                <option value="mood">Mood</option>
              </select>
            </div>

            <Input
              label="Value"
              placeholder="Enter measurement value"
              value={newMetricValue}
              onChange={(e) => setNewMetricValue(e.target.value)}
              fullWidth
            />

            <Input
              label="Notes (optional)"
              placeholder="How are you feeling?"
              fullWidth
            />
          </div>

          <div className="space-y-3">
            <Button
              variant="primary"
              size="xl"
              fullWidth
              onClick={() => {
                // Save metric
                setShowAddModal(false);
                setNewMetricValue('');
              }}
            >
              Save Measurement
            </Button>
            
            <Button
              variant="ghost"
              size="lg"
              fullWidth
              onClick={() => {
                setShowAddModal(false);
                setNewMetricValue('');
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </ElderlyLayout>
  );
};
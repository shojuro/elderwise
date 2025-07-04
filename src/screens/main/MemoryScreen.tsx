import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow, format } from 'date-fns';
import { 
  Search, 
  Filter, 
  Heart, 
  MessageCircle, 
  Calendar,
  Tag,
  Clock,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

// Mock data - replace with actual API calls
const mockMemories = [
  {
    id: '1',
    content: 'Had a wonderful conversation about my garden. The tomatoes are growing beautifully this year, just like my grandmother used to grow them.',
    type: 'interaction' as const,
    tags: ['gardening', 'family', 'memories'],
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    importance: 4,
    category: 'Happy Moments'
  },
  {
    id: '2',
    content: 'Discussed my morning walk and how it helps with my arthritis. The fresh air and gentle exercise make me feel energized.',
    type: 'health' as const,
    tags: ['exercise', 'arthritis', 'wellness'],
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    importance: 3,
    category: 'Health & Wellness'
  },
  {
    id: '3',
    content: 'Feeling a bit lonely today. Missing my late husband John. ElderWise helped me remember the beautiful picnic we had at the lake.',
    type: 'emotion' as const,
    tags: ['loneliness', 'grief', 'memories', 'support'],
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    importance: 5,
    category: 'Emotional Support'
  },
  {
    id: '4',
    content: 'Shared my famous apple pie recipe. Four generations of women in my family have made this pie. The secret is adding a pinch of cardamom.',
    type: 'preference' as const,
    tags: ['cooking', 'family recipes', 'tradition'],
    timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    importance: 4,
    category: 'Traditions'
  },
  {
    id: '5',
    content: 'Today marks my 50th wedding anniversary. Even though John is no longer with me, I celebrated by looking through our photo albums.',
    type: 'event' as const,
    tags: ['anniversary', 'celebration', 'memories'],
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    importance: 5,
    category: 'Special Occasions'
  }
];

const categories = [
  { name: 'All Memories', color: 'lavender' },
  { name: 'Happy Moments', color: 'sage' },
  { name: 'Health & Wellness', color: 'blue' },
  { name: 'Emotional Support', color: 'coral' },
  { name: 'Traditions', color: 'purple' },
  { name: 'Special Occasions', color: 'gold' }
];

export const MemoryScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Memories');
  const [expandedMemory, setExpandedMemory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const filteredMemories = mockMemories.filter(memory => {
    const matchesSearch = memory.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         memory.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'All Memories' || memory.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'health': return Heart;
      case 'emotion': return Heart;
      case 'event': return Calendar;
      default: return MessageCircle;
    }
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 5) return 'text-coral-600';
    if (importance >= 4) return 'text-sage-600';
    return 'text-lavender-600';
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

  return (
    <ElderlyLayout title="Memory Lane">
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
          <h1 className="text-elder-h1 mb-2">Your Memory Lane</h1>
          <p className="text-elder-body text-lavender-600">
            Revisit your meaningful conversations and special moments
          </p>
        </motion.div>

        {/* Search and Filter */}
        <motion.div
          variants={itemVariants}
          className="mb-6 space-y-4 px-4"
        >
          <Input
            placeholder="Search your memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={Search}
            fullWidth
          />

          {/* Category filters */}
          <div className="overflow-x-auto">
            <div className="flex space-x-2 pb-2">
              {categories.map((category) => (
                <Button
                  key={category.name}
                  variant={selectedCategory === category.name ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedCategory(category.name)}
                  className="whitespace-nowrap"
                >
                  {category.name}
                </Button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Results count */}
        <motion.div
          variants={itemVariants}
          className="px-4 mb-4"
        >
          <p className="text-elder-caption">
            {filteredMemories.length} {filteredMemories.length === 1 ? 'memory' : 'memories'} found
          </p>
        </motion.div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" text="Loading your memories..." />
          </div>
        )}

        {/* Memory timeline */}
        <div className="px-4 space-y-4">
          <AnimatePresence>
            {filteredMemories.map((memory, index) => {
              const TypeIcon = getTypeIcon(memory.type);
              const isExpanded = expandedMemory === memory.id;
              
              return (
                <motion.div
                  key={memory.id}
                  variants={itemVariants}
                  layout
                >
                  <Card
                    hover
                    onClick={() => setExpandedMemory(isExpanded ? null : memory.id)}
                    className="cursor-pointer"
                  >
                    <div className="flex items-start space-x-4">
                      {/* Timeline indicator */}
                      <div className="relative">
                        <div className="w-10 h-10 bg-lavender-500 rounded-full flex items-center justify-center">
                          <TypeIcon size={20} className="text-white" />
                        </div>
                        
                        {index < filteredMemories.length - 1 && (
                          <div className="absolute top-10 left-1/2 w-0.5 h-8 bg-lavender-200 -translate-x-0.5" />
                        )}
                      </div>

                      {/* Memory content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-elder-caption text-lavender-600">
                            {memory.category}
                          </span>
                          <div className="flex items-center space-x-2">
                            <Clock size={14} className="text-lavender-400" />
                            <span className="text-elder-caption">
                              {formatDistanceToNow(new Date(memory.timestamp), { addSuffix: true })}
                            </span>
                          </div>
                        </div>

                        <p className={`text-elder-body mb-3 ${isExpanded ? '' : 'line-clamp-2'}`}>
                          {memory.content}
                        </p>

                        {/* Tags */}
                        <div className="flex flex-wrap gap-2 mb-3">
                          {memory.tags.slice(0, isExpanded ? memory.tags.length : 3).map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-lavender-100 text-lavender-700"
                            >
                              <Tag size={12} className="mr-1" />
                              {tag}
                            </span>
                          ))}
                          {!isExpanded && memory.tags.length > 3 && (
                            <span className="text-elder-caption text-lavender-500">
                              +{memory.tags.length - 3} more
                            </span>
                          )}
                        </div>

                        {/* Importance indicator */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <div
                                key={i}
                                className={`w-2 h-2 rounded-full ${
                                  i < memory.importance ? 'bg-sage-500' : 'bg-lavender-200'
                                }`}
                              />
                            ))}
                            <span className="text-elder-caption ml-2">
                              Important memory
                            </span>
                          </div>

                          <Button
                            variant="ghost"
                            size="sm"
                            icon={isExpanded ? ChevronUp : ChevronDown}
                            ariaLabel={isExpanded ? "Collapse" : "Expand"}
                          />
                        </div>

                        {/* Expanded details */}
                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.3 }}
                              className="overflow-hidden"
                            >
                              <div className="pt-4 mt-4 border-t border-lavender-100">
                                <div className="grid grid-cols-2 gap-4 text-elder-caption">
                                  <div>
                                    <span className="font-semibold">Date:</span> {format(new Date(memory.timestamp), 'PPP')}
                                  </div>
                                  <div>
                                    <span className="font-semibold">Type:</span> {memory.type}
                                  </div>
                                </div>
                                
                                <div className="mt-4 flex space-x-2">
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      // Share memory functionality
                                    }}
                                  >
                                    Share
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      // Continue conversation functionality
                                    }}
                                  >
                                    Continue chat
                                  </Button>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {/* Empty state */}
        {filteredMemories.length === 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="w-16 h-16 bg-lavender-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search size={28} className="text-lavender-500" />
            </div>
            <h3 className="text-elder-h3 mb-2">No memories found</h3>
            <p className="text-elder-body text-lavender-600 mb-6">
              Try adjusting your search or category filter
            </p>
            <Button
              variant="primary"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('All Memories');
              }}
            >
              Show all memories
            </Button>
          </motion.div>
        )}
      </motion.div>
    </ElderlyLayout>
  );
};
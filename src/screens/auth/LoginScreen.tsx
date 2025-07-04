import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Heart } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { Card } from '../../components/common/Card';
import { AuthLayout } from '../../components/common/Layout';
import { useAppStore } from '../../store';
import { apiService } from '../../services/api';

interface LoginForm {
  username: string;
  password: string;
  rememberMe: boolean;
}

export const LoginScreen: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    defaultValues: {
      username: '',
      password: '',
      rememberMe: false
    }
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.login({
        username: data.username,
        password: data.password
      });

      if (response.success && response.data) {
        // Store token
        localStorage.setItem('elderwise-token', response.data.token);
        
        // Set user state
        setUser(response.data.user);
        setAuthenticated(true);

        // Navigate based on user role
        if (response.data.user.role === 'family') {
          navigate('/family');
        } else {
          navigate('/chat');
        }
      } else {
        setError(response.error || 'Login failed');
      }
    } catch (error: any) {
      setError(error.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { 
      opacity: 1, 
      scale: 1,
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
    <AuthLayout>
      <motion.div
        className="w-full max-w-md mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Logo and title */}
        <motion.div
          variants={itemVariants}
          className="text-center mb-8"
        >
          <motion.div
            className="w-16 h-16 bg-lavender-500 rounded-full flex items-center justify-center mx-auto mb-4"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Heart size={28} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-2">Welcome Back</h1>
          <p className="text-elder-body text-lavender-600">
            Sign in to continue your conversation with ElderWise
          </p>
        </motion.div>

        {/* Login form */}
        <motion.div variants={itemVariants}>
          <Card>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Error message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-coral-50 border border-coral-200 rounded-elder p-4"
                >
                  <p className="text-coral-700 text-sm-elder">{error}</p>
                </motion.div>
              )}

              {/* Username field */}
              <Input
                label="Username or Email"
                placeholder="Enter your username"
                {...register('username', { 
                  required: 'Username is required',
                  minLength: { value: 3, message: 'Username must be at least 3 characters' }
                })}
                error={errors.username?.message}
                fullWidth
              />

              {/* Password field */}
              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  {...register('password', { 
                    required: 'Password is required',
                    minLength: { value: 6, message: 'Password must be at least 6 characters' }
                  })}
                  error={errors.password?.message}
                  fullWidth
                />
                
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-[52px] text-lavender-500 hover:text-lavender-700"
                >
                  {showPassword ? <EyeOff size={24} /> : <Eye size={24} />}
                </button>
              </div>

              {/* Remember me checkbox */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="rememberMe"
                  {...register('rememberMe')}
                  className="w-5 h-5 text-lavender-600 border-2 border-lavender-300 rounded focus:ring-lavender-500"
                />
                <label htmlFor="rememberMe" className="ml-3 text-elder-body">
                  Remember me
                </label>
              </div>

              {/* Submit button */}
              <Button
                type="submit"
                fullWidth
                size="xl"
                loading={isLoading}
                disabled={isLoading}
              >
                Sign In
              </Button>
            </form>
          </Card>
        </motion.div>

        {/* Additional options */}
        <motion.div
          variants={itemVariants}
          className="mt-8 text-center space-y-4"
        >
          <Link
            to="/forgot-password"
            className="text-lavender-600 hover:text-lavender-800 text-base-elder"
          >
            Forgot your password?
          </Link>

          <div className="flex items-center justify-center space-x-2">
            <span className="text-elder-body text-lavender-600">Don't have an account?</span>
            <Link
              to="/setup"
              className="text-lavender-700 hover:text-lavender-900 font-semibold text-base-elder"
            >
              Get started
            </Link>
          </div>

          <div className="pt-6 border-t border-lavender-100">
            <p className="text-elder-caption text-lavender-500">
              Need help? Call support: <br />
              <a href="tel:1-800-ELDER-WISE" className="font-semibold text-lavender-700">
                1-800-ELDER-WISE
              </a>
            </p>
          </div>
        </motion.div>

        {/* Family member access */}
        <motion.div
          variants={itemVariants}
          className="mt-8"
        >
          <Card className="bg-sage-50 border-sage-200">
            <div className="text-center">
              <p className="text-elder-body text-sage-800 mb-4">
                Are you a family member?
              </p>
              <Button
                variant="secondary"
                onClick={() => navigate('/family/login')}
                size="lg"
                fullWidth
              >
                Family Member Access
              </Button>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AuthLayout>
  );
};
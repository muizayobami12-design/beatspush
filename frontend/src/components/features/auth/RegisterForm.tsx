'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/authService';
import { Turnstile } from '@/components/security/Turnstile';
import { getDeviceId, getDeviceInfo } from '@/services/fingerprintService';
import { validateRegistrationEmail } from '@/services/emailValidationService';

const registerSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
  role: z.enum(['artist', 'dj', 'producer', 'fan']),
  country: z.string().min(1, 'Please select your country'),
  location: z.string().optional().or(z.literal('')),
  bio: z.string().max(500, 'Bio must be 500 characters or less').optional().or(z.literal('')),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRoleState, setSelectedRoleState] = useState<string>('');
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [emailSuggestion, setEmailSuggestion] = useState<string | null>(null);
  const login = useAuthStore((state) => state.login);

  // Get device fingerprint on mount
  useEffect(() => {
    getDeviceId().then(setDeviceId);
  }, []);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    trigger,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: undefined as any,
      country: '',
      location: '',
      bio: '',
    },
  });

  const nextStep = async () => {
    if (step === 1) {
      const isValid = await trigger(['email', 'password', 'confirmPassword', 'fullName']);
      if (isValid) {
        // Validate email before proceeding
        const email = watch('email');
        const emailValidation = await validateRegistrationEmail(email);
        
        if (!emailValidation.valid) {
          setError(emailValidation.reason || 'Invalid email address');
          return;
        }
        
        if (emailValidation.suggestions && emailValidation.suggestions.length > 0) {
          setEmailSuggestion(emailValidation.suggestions[0]);
        } else {
          setEmailSuggestion(null);
        }
        
        setStep(2);
        setError(null);
      }
    } else if (step === 2) {
      if (selectedRoleState) {
        setStep(3);
        setError(null);
      } else {
        setError('Please select a role');
      }
    } else {
      setStep(step + 1);
      setError(null);
    }
  };

  const prevStep = () => {
    setStep(step - 1);
    setError(null);
  };

  const handleRoleSelect = (roleValue: string) => {
    setSelectedRoleState(roleValue);
    setValue('role', roleValue as any);
    setError(null);
    // Auto-advance to step 3 after a brief visual feedback
    setTimeout(() => {
      setStep(3);
    }, 250);
  };

  const onSubmit = async (data: RegisterFormData) => {
    // Check if Turnstile token is available
    if (!turnstileToken) {
      setError('Please complete the security check');
      return;
    }

    setIsLoading(true);
    setError(null);

    console.log('Registration data:', data);

    try {
      // Get detailed device info for fraud detection
      const deviceInfo = await getDeviceInfo();
      
      const response = await authService.register({
        email: data.email,
        password: data.password,
        full_name: data.fullName,
        role: data.role,
        location: data.country + (data.location ? ', ' + data.location : ''),
        bio: data.bio || undefined,
        // Security metadata
        turnstile_token: turnstileToken,
        device_id: deviceId || undefined,
        device_info: deviceInfo ? JSON.stringify(deviceInfo) : undefined,
      });
      
      console.log('Registration response:', response);
      
      // Auto-login after successful registration
      login(response.user, response.token);
      
      console.log('Redirecting to dashboard...');
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Registration error:', err);
      if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Cannot connect to server. Please make sure the backend is running on port 9000.');
      } else {
        const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
        setError(Array.isArray(errorMessage) ? errorMessage[0]?.msg || errorMessage[0] : errorMessage);
      }
      // Reset Turnstile on error
      setTurnstileToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const roles = [
    { value: 'artist', label: '🎤 Artist', description: 'Create and promote your music' },
    { value: 'dj', label: '🎧 DJ', description: 'Curate playlists and manage events' },
    { value: 'producer', label: '🎹 Producer', description: 'Sell beats and manage licensing' },
    { value: 'fan', label: '🎵 Fan', description: 'Discover and support creators' },
  ];

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
          Create Account
        </h1>
        <p className="text-muted-foreground">
          Join BeatPush and start promoting your music
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="flex items-center justify-center space-x-2">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={`h-2 w-16 rounded-full transition-colors ${
              s === step
                ? 'bg-gradient-to-r from-[#667eea] to-[#764ba2]'
                : s < step
                ? 'bg-primary'
                : 'bg-muted'
            }`}
          />
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20">
            {error}
          </div>
        )}

        {/* Step 1: Credentials */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="fullName" className="text-sm font-medium">
                Full Name
              </label>
              <Input
                id="fullName"
                placeholder="John Doe"
                {...register('fullName')}
                aria-invalid={!!errors.fullName}
              />
              {errors.fullName && (
                <p className="text-sm text-destructive">{errors.fullName.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                {...register('email')}
                aria-invalid={!!errors.email}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
              {emailSuggestion && (
                <p className="text-sm text-primary">{emailSuggestion}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                {...register('password')}
                aria-invalid={!!errors.password}
              />
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirm Password
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                {...register('confirmPassword')}
                aria-invalid={!!errors.confirmPassword}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button
              type="button"
              onClick={nextStep}
              className="w-full bg-gradient-to-r from-[#667eea] to-[#764ba2]"
            >
              Continue
            </Button>
          </div>
        )}

        {/* Step 2: Role Selection */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="space-y-3">
              <label className="text-sm font-medium">Choose Your Role (tap to select & continue)</label>
              <div className="grid grid-cols-2 gap-3">
                {roles.map((role) => (
                  <div
                    key={role.value}
                    onClick={() => handleRoleSelect(role.value)}
                    className={`relative flex flex-col items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98] ${
                      selectedRoleState === role.value
                        ? 'border-primary bg-primary/10 ring-2 ring-primary/30'
                        : 'border-muted hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium text-lg">{role.label}</span>
                    <span className="text-xs text-muted-foreground text-center mt-1">
                      {role.description}
                    </span>
                    {selectedRoleState === role.value && (
                      <div className="absolute top-1 right-1 w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex space-x-3">
              <Button type="button" onClick={prevStep} variant="outline" className="flex-1">
                Back
              </Button>
              <Button
                type="button"
                onClick={nextStep}
                className="flex-1 bg-gradient-to-r from-[#667eea] to-[#764ba2]"
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Location & Optional Profile Info */}
        {step === 3 && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              Tell us where you're from
            </p>

            <div className="space-y-2">
              <label htmlFor="country" className="text-sm font-medium">
                Country <span className="text-destructive">*</span>
              </label>
              <select
                id="country"
                {...register('country')}
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Select your country</option>
                <option value="Nigeria">Nigeria</option>
                <option value="Ghana">Ghana</option>
                <option value="Kenya">Kenya</option>
                <option value="South Africa">South Africa</option>
                <option value="Tanzania">Tanzania</option>
                <option value="Uganda">Uganda</option>
                <option value="Rwanda">Rwanda</option>
                <option value="Senegal">Senegal</option>
                <option value="Ivory Coast">Ivory Coast</option>
                <option value="Cameroon">Cameroon</option>
                <option value="Ethiopia">Ethiopia</option>
                <option value="Zimbabwe">Zimbabwe</option>
                <option value="Zambia">Zambia</option>
                <option value="Botswana">Botswana</option>
                <option value="Namibia">Namibia</option>
                <option value="Other">Other Country</option>
              </select>
              {errors.country && (
                <p className="text-sm text-destructive">{errors.country.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="location" className="text-sm font-medium">
                City (Optional)
              </label>
              <Input
                id="location"
                placeholder="Lagos, Accra, Nairobi..."
                {...register('location')}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="bio" className="text-sm font-medium">
                Bio (Optional) ({(watch('bio') || '').length}/500)
              </label>
              <textarea
                id="bio"
                placeholder="Tell us about yourself..."
                {...register('bio')}
                rows={4}
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {errors.bio && (
                <p className="text-sm text-destructive">{errors.bio.message}</p>
              )}
            </div>

            {/* Security Check (Turnstile CAPTCHA) */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Security Check</label>
              <Turnstile
                onSuccess={(token) => {
                  setTurnstileToken(token);
                  setError(null);
                }}
                onError={() => setError('Security check failed. Please try again.')}
                onExpire={() => {
                  setTurnstileToken(null);
                  setError('Security check expired. Please complete it again.');
                }}
              />
            </div>

            <div className="flex space-x-3">
              <Button type="button" onClick={prevStep} variant="outline" className="flex-1">
                Back
              </Button>
              <Button
                type="submit"
                disabled={isLoading || !turnstileToken}
                className="flex-1 bg-gradient-to-r from-[#667eea] to-[#764ba2]"
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </div>
          </div>
        )}
      </form>

      <div className="text-center text-sm">
        <span className="text-muted-foreground">Already have an account? </span>
        <Link href="/login" className="text-primary hover:underline font-medium">
          Sign in
        </Link>
      </div>
    </div>
  );
}

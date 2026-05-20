import { Check } from "lucide-react";

interface Step {
  number: number;
  title: string;
}

interface ProgressIndicatorProps {
  currentStep: number;
  steps: Step[];
}

export function ProgressIndicator({ currentStep, steps }: ProgressIndicatorProps) {
  return (
    <div className="mb-12">
      <div className="flex items-center justify-center gap-2 md:gap-4">
        {steps.map((step, index) => (
          <div key={step.number} className="flex items-center">
            <div className="flex flex-col items-center gap-2">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-full border-2 transition-all duration-500 shadow-lg ${
                  currentStep > step.number
                    ? "border-primary/50 bg-primary/20 text-primary ring-1 ring-primary/50 backdrop-blur-md"
                    : currentStep === step.number
                    ? "border-primary bg-primary text-primary-foreground shadow-[0_0_20px_rgba(124,58,237,0.5)] scale-110"
                    : "border-white/10 bg-white/5 text-muted-foreground backdrop-blur-md"
                }`}
                data-testid={`step-indicator-${step.number}`}
              >
                {currentStep > step.number ? (
                  <Check className="h-6 w-6 stroke-[3]" />
                ) : (
                  <span className="text-base font-bold">{step.number}</span>
                )}
              </div>
              <span
                className={`hidden text-sm font-medium tracking-wide md:block mt-2 transition-colors duration-300 ${
                  currentStep >= step.number ? "text-foreground" : "text-muted-foreground"
                }`}
              >
                {step.title}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="relative mx-2 md:mx-6 h-1 w-12 md:w-24 bg-white/5 rounded-full overflow-hidden">
                <div
                  className={`absolute top-0 left-0 h-full bg-gradient-to-r from-primary to-secondary transition-all duration-700 ease-out`}
                  style={{ width: currentStep > step.number ? '100%' : '0%' }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

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
                className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors ${
                  currentStep > step.number
                    ? "border-primary bg-primary text-primary-foreground"
                    : currentStep === step.number
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background text-muted-foreground"
                }`}
                data-testid={`step-indicator-${step.number}`}
              >
                {currentStep > step.number ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-semibold">{step.number}</span>
                )}
              </div>
              <span
                className={`hidden text-sm md:block ${
                  currentStep >= step.number ? "text-foreground" : "text-muted-foreground"
                }`}
              >
                {step.title}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`mx-2 h-0.5 w-12 md:mx-4 md:w-20 ${
                  currentStep > step.number ? "bg-primary" : "bg-border"
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

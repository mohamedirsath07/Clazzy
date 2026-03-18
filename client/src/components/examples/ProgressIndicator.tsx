import { ProgressIndicator } from "../ProgressIndicator";

const steps = [
  { number: 1, title: "Upload" },
  { number: 2, title: "Details" },
  { number: 3, title: "Results" },
];

export default function ProgressIndicatorExample() {
  return (
    <div className="p-8">
      <ProgressIndicator currentStep={2} steps={steps} />
    </div>
  );
}

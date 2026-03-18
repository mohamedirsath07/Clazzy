import { UserDetailsForm } from "../UserDetailsForm";

export default function UserDetailsFormExample() {
  return (
    <div className="p-8">
      <UserDetailsForm 
        onSubmit={(data) => console.log("Form submitted:", data)}
      />
    </div>
  );
}

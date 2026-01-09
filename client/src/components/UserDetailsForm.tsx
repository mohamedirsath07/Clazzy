import { useForm } from "react-hook-form";
import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { userProfileSchema, type UserProfile } from "@shared/schema";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

interface UserDetailsFormProps {
  onSubmit: (data: UserProfile) => void;
  defaultValues?: Partial<UserProfile>;
}

export function UserDetailsForm({ onSubmit, defaultValues }: UserDetailsFormProps) {
  const form = useForm<UserProfile>({
    resolver: zodResolver(userProfileSchema),
    defaultValues: {
      name: defaultValues?.name || "",
      age: defaultValues?.age || undefined,
      gender: defaultValues?.gender || "other",
    },
  });

  // Auto-submit when form values change
  const watchedValues = form.watch();

  // Submit form when all required fields are filled
  useEffect(() => {
    const { name, age, gender } = watchedValues;
    if (name && age && gender) {
      onSubmit({ name, age, gender });
    }
  }, [watchedValues, onSubmit]);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Enter your name"
                    {...field}
                    data-testid="input-name"
                    className="h-12 rounded-xl"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="age"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Age</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="Enter your age"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                    data-testid="input-age"
                    className="h-12 rounded-xl"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="gender"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Gender</FormLabel>
              <FormControl>
                <div className="flex gap-3">
                  {(["male", "female", "other"] as const).map((gender) => (
                    <Button
                      key={gender}
                      type="button"
                      variant={field.value === gender ? "default" : "outline"}
                      className="flex-1 rounded-full capitalize"
                      onClick={() => field.onChange(gender)}
                      data-testid={`button-gender-${gender}`}
                    >
                      {gender}
                    </Button>
                  ))}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}

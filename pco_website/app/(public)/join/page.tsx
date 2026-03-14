"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { apiFetch } from "@/lib/api";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { SectionTitle } from "@/components/ui/SectionTitle";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(1, "Phone number is required"),
  graduation_year: z
    .string()
    .min(4, "Enter your 4-digit graduation year")
    .max(4, "Enter your 4-digit graduation year")
    .regex(/^\d{4}$/, "Enter a valid year (e.g. 2027)"),
  major: z.string().min(1, "Major is required"),
});

type FormData = z.infer<typeof schema>;

export default function JoinPage() {
  const [success, setSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      await apiFetch("/v1/interest", {
        method: "POST",
        body: JSON.stringify(data),
      });
      setSuccess(true);
    } catch (err: unknown) {
      if ((err as { status?: number }).status === 409) {
        setError("email", { message: "Looks like you've already signed up!" });
      }
    }
  };

  if (success) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 text-center">
        <SectionTitle>You&apos;re on our list!</SectionTitle>
        <p className="mt-4 text-white/60 font-body text-lg max-w-md">
          We&apos;ll reach out when rush begins.
        </p>
        <div className="mt-8">
          <ChromeButton href="/" variant="secondary">Back to Home</ChromeButton>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-16">
      <SectionTitle>Join the Interest List</SectionTitle>
      <form onSubmit={handleSubmit(onSubmit)} className="mt-10 flex flex-col gap-6">

        <div className="flex flex-col gap-1.5">
          <label htmlFor="name" className="text-sm tracking-widest uppercase text-white/60">
            Name
          </label>
          <input
            id="name"
            type="text"
            {...register("name")}
            className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
            aria-describedby={errors.name ? "name-error" : undefined}
            aria-invalid={!!errors.name}
          />
          {errors.name && (
            <p id="name-error" className="text-xs text-red-400">{errors.name.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-sm tracking-widest uppercase text-white/60">
            Email
          </label>
          <input
            id="email"
            type="email"
            {...register("email")}
            className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
            aria-describedby={errors.email ? "email-error" : undefined}
            aria-invalid={!!errors.email}
          />
          {errors.email && (
            <p id="email-error" className="text-xs text-red-400">{errors.email.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="phone" className="text-sm tracking-widest uppercase text-white/60">
            Phone
          </label>
          <input
            id="phone"
            type="tel"
            {...register("phone")}
            className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
            aria-describedby={errors.phone ? "phone-error" : undefined}
            aria-invalid={!!errors.phone}
          />
          {errors.phone && (
            <p id="phone-error" className="text-xs text-red-400">{errors.phone.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="graduation_year" className="text-sm tracking-widest uppercase text-white/60">
            Graduation Year
          </label>
          <input
            id="graduation_year"
            type="text"
            placeholder="e.g. 2027"
            {...register("graduation_year")}
            className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
            aria-describedby={errors.graduation_year ? "graduation_year-error" : undefined}
            aria-invalid={!!errors.graduation_year}
          />
          {errors.graduation_year && (
            <p id="graduation_year-error" className="text-xs text-red-400">{errors.graduation_year.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="major" className="text-sm tracking-widest uppercase text-white/60">
            Major
          </label>
          <input
            id="major"
            type="text"
            {...register("major")}
            className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
            aria-describedby={errors.major ? "major-error" : undefined}
            aria-invalid={!!errors.major}
          />
          {errors.major && (
            <p id="major-error" className="text-xs text-red-400">{errors.major.message}</p>
          )}
        </div>

        <ChromeButton
          type="submit"
          variant="primary"
          className="w-full justify-center mt-2"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Submitting..." : "Submit"}
        </ChromeButton>

      </form>
    </div>
  );
}

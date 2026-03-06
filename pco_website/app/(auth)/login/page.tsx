import { LoginForm } from "@/components/auth/LoginForm";

export const metadata = {
  title: "Login | Psi Chi Omega",
};

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <LoginForm />
    </div>
  );
}

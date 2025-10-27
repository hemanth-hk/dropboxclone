"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authAPI } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { AxiosError } from "axios";
import { ApiError } from "@/lib/types";

export function LoginForm() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    userName: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Login and get tokens
      const tokenResponse = await authAPI.login(formData);
      setTokens(tokenResponse.access_token, tokenResponse.refresh_token);

      // Register the user (get user info from register endpoint response)
      // Since we don't have a "me" endpoint, we'll store basic info
      // In a real app, you'd fetch user info after login
      setUser({
        id: 0, // Will be set after first API call
        userName: formData.userName,
        displayName: formData.userName,
        created: new Date().toISOString(),
        modified: new Date().toISOString(),
      });

      toast.success("Login successful!");
      router.push("/dashboard");
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      const message = axiosError.response?.data?.detail || "Login failed";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-4">
      <div className="space-y-2">
        <Label htmlFor="login-username">Username</Label>
        <Input
          id="login-username"
          type="text"
          placeholder="Enter your username"
          value={formData.userName}
          onChange={(e) =>
            setFormData({ ...formData, userName: e.target.value })
          }
          required
          disabled={isLoading}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="login-password">Password</Label>
        <Input
          id="login-password"
          type="password"
          placeholder="Enter your password"
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          required
          disabled={isLoading}
        />
      </div>
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Logging in..." : "Login"}
      </Button>
    </form>
  );
}


"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuthStore } from "@/store/auth-store";
import { FileIcon, Upload, Download, Shield, ArrowRight } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, initializeAuth, isLoading } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <div className="container mx-auto px-4 py-16 max-w-6xl">
        {/* Header */}
        <nav className="flex items-center justify-between mb-20">
          <div className="text-3xl font-bold text-foreground">
            TypeBox
          </div>
          <Link href="/auth">
            <Button>Get Started</Button>
          </Link>
        </nav>

        {/* Hero Section */}
        <div className="text-center mb-20">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
            Secure File Storage
            <br />
            <span className="text-foreground">
              Made Simple
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Store, manage, and access your files from anywhere. Fast, secure,
            and easy to use.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/auth">
              <Button size="lg" className="text-lg">
                Start Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          <Card className="p-6">
            <div className="p-3 bg-muted rounded-lg w-fit mb-4">
              <Upload className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Easy Upload</h3>
            <p className="text-muted-foreground">
              Drag and drop your files or browse to upload. Simple and
              intuitive.
            </p>
          </Card>

          <Card className="p-6">
            <div className="p-3 bg-muted rounded-lg w-fit mb-4">
              <Shield className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure Storage</h3>
            <p className="text-muted-foreground">
              Your files are encrypted and protected with industry-standard
              security.
            </p>
          </Card>

          <Card className="p-6">
            <div className="p-3 bg-muted rounded-lg w-fit mb-4">
              <Download className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Quick Access</h3>
            <p className="text-muted-foreground">
              Download your files anytime, anywhere with one click.
            </p>
          </Card>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Card className="p-12 border-2">
            <div className="max-w-2xl mx-auto">
              <FileIcon className="h-12 w-12 mx-auto mb-4" />
              <h2 className="text-3xl font-bold mb-4">
                Ready to get started?
              </h2>
              <p className="text-muted-foreground mb-6">
                Join thousands of users who trust TypeBox with their files.
              </p>
              <Link href="/auth">
                <Button size="lg" className="text-lg">
                  Create Account
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

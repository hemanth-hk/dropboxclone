"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/dashboard/Navbar";
import { FileUploadZone } from "@/components/dashboard/FileUploadZone";
import { FilesTable } from "@/components/dashboard/FilesTable";
import { useAuthStore } from "@/store/auth-store";
import { filesAPI } from "@/lib/api";
import { FileInfo } from "@/lib/types";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, initializeAuth, isLoading: authLoading } = useAuthStore();
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isAuthenticated, authLoading, router]);

  const fetchFiles = async () => {
    setIsLoadingFiles(true);
    try {
      const response = await filesAPI.list(page, pageSize);
      setFiles(response.files);
      setTotal(response.total);
    } catch (error) {
      toast.error("Failed to fetch files");
      console.error("Error fetching files:", error);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchFiles();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, isAuthenticated]);

  const handleUploadSuccess = () => {
    // Refresh the files list after successful upload
    setPage(1);
    fetchFiles();
  };

  const handleDeleteSuccess = () => {
    // Refresh the files list after successful deletion
    fetchFiles();
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">My Files</h1>
            <p className="text-muted-foreground">
              Upload, manage, and download your files
            </p>
          </div>

          <FileUploadZone onUploadSuccess={handleUploadSuccess} />

          <FilesTable
            files={files}
            total={total}
            page={page}
            pageSize={pageSize}
            isLoading={isLoadingFiles}
            onPageChange={setPage}
            onDeleteSuccess={handleDeleteSuccess}
          />
        </div>
      </main>
    </div>
  );
}


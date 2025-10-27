"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { DeleteConfirmDialog } from "./DeleteConfirmDialog";
import { FileInfo } from "@/lib/types";
import { filesAPI } from "@/lib/api";
import { formatFileSize, formatDate } from "@/lib/utils";
import { Download, Trash2, ChevronLeft, ChevronRight, FileIcon } from "lucide-react";
import { toast } from "sonner";

interface FilesTableProps {
  files: FileInfo[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onDeleteSuccess: () => void;
}

export function FilesTable({
  files,
  total,
  page,
  pageSize,
  isLoading,
  onPageChange,
  onDeleteSuccess,
}: FilesTableProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<FileInfo | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const totalPages = Math.ceil(total / pageSize);
  const startIndex = (page - 1) * pageSize + 1;
  const endIndex = Math.min(page * pageSize, total);

  const handleDownload = async (file: FileInfo) => {
    try {
      await filesAPI.download(file.id, file.fileName);
      toast.success("Download started");
    } catch (error) {
      toast.error("Failed to download file");
      console.error("Download error:", error);
    }
  };

  const handleDeleteClick = (file: FileInfo) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!fileToDelete) return;

    setIsDeleting(true);
    try {
      await filesAPI.delete(fileToDelete.id);
      toast.success("File deleted successfully");
      setDeleteDialogOpen(false);
      setFileToDelete(null);
      onDeleteSuccess();
    } catch (error) {
      toast.error("Failed to delete file");
      console.error("Delete error:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const getFileTypeColor = (fileType: string) => {
    if (fileType.startsWith("image/")) return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
    if (fileType.startsWith("video/")) return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300";
    if (fileType.startsWith("audio/")) return "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300";
    if (fileType.includes("pdf")) return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
    if (fileType.includes("text")) return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300";
  };

  const getFileTypeLabel = (fileType: string) => {
    const parts = fileType.split("/");
    return parts[parts.length - 1].toUpperCase();
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
          ))}
        </div>
      </Card>
    );
  }

  if (files.length === 0) {
    return (
      <Card className="p-12">
        <div className="flex flex-col items-center justify-center text-center space-y-3">
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full">
            <FileIcon className="h-8 w-8 text-gray-400" />
          </div>
          <div>
            <h3 className="text-lg font-medium mb-1">No files yet</h3>
            <p className="text-sm text-muted-foreground">
              Upload your first file to get started
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <div className="overflow-x-auto p-6">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>File Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Uploaded</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {files.map((file) => (
                <TableRow key={file.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {file.fileName}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="secondary"
                      className={getFileTypeColor(file.fileType)}
                    >
                      {getFileTypeLabel(file.fileType)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatFileSize(file.fileSize)}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(file.created)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDownload(file)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeleteClick(file)}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex}-{endIndex} of {total} files
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => onPageChange(page - 1)}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <div className="text-sm font-medium">
              Page {page} of {totalPages || 1}
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </Card>

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        fileName={fileToDelete?.fileName || ""}
        onConfirm={handleDeleteConfirm}
        isDeleting={isDeleting}
      />
    </>
  );
}


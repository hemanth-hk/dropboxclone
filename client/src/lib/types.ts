// API Response & Request Types

export interface User {
  id: number;
  displayName: string;
  userName: string;
  created: string;
  modified: string;
}

export interface LoginRequest {
  userName: string;
  password: string;
}

export interface SignupRequest {
  displayName: string;
  userName: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface FileInfo {
  id: number;
  fileName: string;
  fileType: string;
  fileSize: number;
  created: string;
}

export interface FileListResponse {
  files: FileInfo[];
  total: number;
  page: number;
  page_size: number;
}

export interface FileUploadResponse {
  id: number;
  fileName: string;
  fileType: string;
  fileSize: number;
  filePath: string;
  message: string;
}

export interface FileDeleteResponse {
  message: string;
}

export interface ApiError {
  detail: string;
}


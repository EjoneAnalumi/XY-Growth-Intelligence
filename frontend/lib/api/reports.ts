import { apiRequest } from "@/lib/api/client";

export type ReportStatus = "draft" | "review" | "approved" | "archived";

export type Report = {
  id: string;
  companyId: string;
  companyName: string;
  domain: string;
  title: string;
  status: ReportStatus;
  storageBucket: string;
  storagePath: string;
  downloadUrl: string | null;
  htmlPreview: string;
  createdAt: string;
  updatedAt: string;
  reviewedAt: string | null;
  approvedAt: string | null;
  archivedAt: string | null;
};

type ReportApiResponse = {
  id: string;
  company_id: string;
  company_name: string;
  domain: string;
  title: string;
  status: ReportStatus;
  storage_bucket: string;
  storage_path: string;
  download_url: string | null;
  html_preview: string;
  created_at: string;
  updated_at: string;
  reviewed_at: string | null;
  approved_at: string | null;
  archived_at: string | null;
};

type ReportListApiResponse = {
  items: ReportApiResponse[];
  total: number;
};

export type ReportDownload = {
  id: string;
  filename: string;
  contentType: string;
  storageBucket: string;
  storagePath: string;
  sizeBytes: number;
  contentBase64: string;
};

type ReportDownloadApiResponse = {
  id: string;
  filename: string;
  content_type: string;
  storage_bucket: string;
  storage_path: string;
  size_bytes: number;
  content_base64: string;
};

const demoReportPayload = {
  company_id: "10000000-0000-4000-8000-000000000001",
  company_name: "Northstar Commerce Group",
  domain: "demo.xy-cyber.example",
  scan_summary: "Approved demo snapshot with SPF pass, DMARC monitoring, and missing CSP.",
};

export async function listReports() {
  const response = await apiRequest<ReportListApiResponse>("/reports");
  return {
    items: response.items.map(mapReport),
    total: response.total,
  };
}

export async function generateDemoReport() {
  return mapReport(
    await apiRequest<ReportApiResponse>("/reports/generate", {
      method: "POST",
      body: JSON.stringify(demoReportPayload),
    })
  );
}

export async function submitReportForReview(reportId: string) {
  return mapReport(
    await apiRequest<ReportApiResponse>(`/reports/${reportId}/review`, {
      method: "POST",
      body: JSON.stringify({ note: "Ready for management review." }),
    })
  );
}

export async function approveReport(reportId: string) {
  return mapReport(
    await apiRequest<ReportApiResponse>(`/reports/${reportId}/approve`, {
      method: "POST",
      body: JSON.stringify({ note: "Approved for internal demo." }),
    })
  );
}

export async function archiveReport(reportId: string) {
  return mapReport(
    await apiRequest<ReportApiResponse>(`/reports/${reportId}/archive`, {
      method: "POST",
      body: JSON.stringify({ note: "Archived after review." }),
    })
  );
}

export async function downloadReport(reportId: string): Promise<ReportDownload> {
  const response = await apiRequest<ReportDownloadApiResponse>(`/reports/${reportId}/download`);
  return {
    id: response.id,
    filename: response.filename,
    contentType: response.content_type,
    storageBucket: response.storage_bucket,
    storagePath: response.storage_path,
    sizeBytes: response.size_bytes,
    contentBase64: response.content_base64,
  };
}

function mapReport(report: ReportApiResponse): Report {
  return {
    id: report.id,
    companyId: report.company_id,
    companyName: report.company_name,
    domain: report.domain,
    title: report.title,
    status: report.status,
    storageBucket: report.storage_bucket,
    storagePath: report.storage_path,
    downloadUrl: report.download_url,
    htmlPreview: report.html_preview,
    createdAt: report.created_at,
    updatedAt: report.updated_at,
    reviewedAt: report.reviewed_at,
    approvedAt: report.approved_at,
    archivedAt: report.archived_at,
  };
}

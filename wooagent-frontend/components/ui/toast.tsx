"use client"

import { toast as sonnerToast } from "sonner"

type ToastProps = {
  title: string
  description?: string
  variant?: "default" | "destructive" | "success"
}

export const toast = {
  success: ({ title, description }: Omit<ToastProps, "variant">) => {
    return sonnerToast.success(title, {
      description,
      position: "top-left",
      className: "rtl",
    })
  },
  error: ({ title, description }: Omit<ToastProps, "variant">) => {
    return sonnerToast.error(title, {
      description,
      position: "top-left",
      className: "rtl",
    })
  },
  info: ({ title, description }: Omit<ToastProps, "variant">) => {
    return sonnerToast(title, {
      description,
      position: "top-left",
      className: "rtl",
    })
  },
} 
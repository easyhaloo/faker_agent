import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 合并 Tailwind CSS 类名的工具函数
 * 结合 clsx 和 tailwind-merge 实现更好的类名合并
 * @param  {...any} inputs 
 * @returns {string} 合并后的类名字符串
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
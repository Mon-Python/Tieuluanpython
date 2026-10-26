/**
 * Type definitions mirroring base_models.py and Member B requirements
 */

export type Role = 'admin' | 'user';

export type DifficultyLevel = 'de' | 'kho';

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
  salt: string;
  passwordHash: string;
  createdAt: string;
}

export interface Subject {
  id: string;
  name: string;
  description: string;
  createdAt: string;
}

export interface Topic {
  id: string;
  subjectId: string;
  name: string;
  createdAt: string;
}

export interface Option {
  id: string;
  content: string;
  isCorrect: boolean;
}

export interface Question {
  id: string;
  topicId: string;
  content: string;
  difficulty: DifficultyLevel;
  options: Option[];
  createdAt: string;
}

export interface Exam {
  id: string;
  subjectId: string;
  title: string;
  seed: number;
  questionIds: string[];
}

export interface ValidationResult {
  isValid: boolean;
  message: string;
}

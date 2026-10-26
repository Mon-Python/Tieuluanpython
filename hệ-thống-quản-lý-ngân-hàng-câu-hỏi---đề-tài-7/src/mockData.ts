import { Subject, Topic, Question, User, Exam } from './types';

export const INITIAL_SUBJECTS: Subject[] = [
  {
    id: 'subj_py01',
    name: 'Lập trình Python',
    description: 'Cơ sở lập trình, hàm, cấu trúc dữ liệu và xử lý file',
    createdAt: '2026-10-15T08:00:00'
  },
  {
    id: 'subj_db02',
    name: 'Cơ sở dữ liệu',
    description: 'Hệ quản trị CSDL, mô hình thực thể và đại số quan hệ',
    createdAt: '2026-10-16T09:30:00'
  },
  {
    id: 'subj_net03',
    name: 'Mạng máy tính',
    description: 'Mô hình OSI, giao thức TCP/IP, định tuyến và an ninh mạng',
    createdAt: '2026-10-18T10:15:00'
  }
];

export const INITIAL_TOPICS: Topic[] = [
  {
    id: 'topic_py_basic',
    subjectId: 'subj_py01',
    name: 'Cú pháp & Kiểu dữ liệu',
    createdAt: '2026-10-15T08:05:00'
  },
  {
    id: 'topic_py_loops',
    subjectId: 'subj_py01',
    name: 'Vòng lặp & Cấu trúc rẽ nhánh',
    createdAt: '2026-10-15T08:10:00'
  },
  {
    id: 'topic_py_funcs',
    subjectId: 'subj_py01',
    name: 'Hàm & Module nâng cao',
    createdAt: '2026-10-15T08:15:00'
  },
  {
    id: 'topic_db_model',
    subjectId: 'subj_db02',
    name: 'Mô hình quan hệ & Khóa',
    createdAt: '2026-10-16T09:35:00'
  },
  {
    id: 'topic_db_sql',
    subjectId: 'subj_db02',
    name: 'Ngôn ngữ truy vấn SQL',
    createdAt: '2026-10-16T09:40:00'
  },
  {
    id: 'topic_net_osi',
    subjectId: 'subj_net03',
    name: 'Mô hình 7 tầng OSI & TCP/IP',
    createdAt: '2026-10-18T10:20:00'
  }
];

export const INITIAL_QUESTIONS: Question[] = [
  {
    id: 'q_a1b2c3d4',
    topicId: 'topic_py_basic',
    content: 'Từ khóa nào dùng để định nghĩa một hàm trong Python?',
    difficulty: 'de',
    options: [
      { id: 'opt_1', content: 'def', isCorrect: true },
      { id: 'opt_2', content: 'function', isCorrect: false },
      { id: 'opt_3', content: 'define', isCorrect: false },
      { id: 'opt_4', content: 'fun', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:20:00'
  },
  {
    id: 'q_e5f60718',
    topicId: 'topic_py_basic',
    content: 'Kiểu dữ liệu nào trong các kiểu sau của Python là kiểu bất biến (immutable)?',
    difficulty: 'de',
    options: [
      { id: 'opt_5', content: 'list', isCorrect: false },
      { id: 'opt_6', content: 'tuple', isCorrect: true },
      { id: 'opt_7', content: 'dict', isCorrect: false },
      { id: 'opt_8', content: 'set', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:25:00'
  },
  {
    id: 'q_9a0b1c2d',
    topicId: 'topic_py_loops',
    content: 'Đặc điểm nào sau đây là ĐÚNG về vòng lặp for trong Python?',
    difficulty: 'de',
    options: [
      { id: 'opt_9', content: 'for lặp tuần tự qua các phần tử của một iterable', isCorrect: true },
      { id: 'opt_10', content: 'for kiểm tra điều kiện trước khi bắt đầu', isCorrect: false },
      { id: 'opt_11', content: 'while không thể kết hợp với lệnh break', isCorrect: false },
      { id: 'opt_12', content: 'for chỉ có thể duyệt qua danh sách số nguyên', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:30:00'
  },
  {
    id: 'q_3e4f5061',
    topicId: 'topic_py_loops',
    content: 'Từ khóa nào dùng để bỏ qua lần lặp hiện tại và chuyển ngay sang lần lặp kế tiếp?',
    difficulty: 'de',
    options: [
      { id: 'opt_13', content: 'break', isCorrect: false },
      { id: 'opt_14', content: 'continue', isCorrect: true },
      { id: 'opt_15', content: 'pass', isCorrect: false },
      { id: 'opt_16', content: 'return', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:35:00'
  },
  {
    id: 'q_728394a5',
    topicId: 'topic_py_funcs',
    content: 'Cơ chế nào cho phép một hàm Python nhận vào số lượng đối số vị trí tùy ý?',
    difficulty: 'kho',
    options: [
      { id: 'opt_17', content: '*args', isCorrect: true },
      { id: 'opt_18', content: '**kwargs', isCorrect: false },
      { id: 'opt_19', content: '&params', isCorrect: false },
      { id: 'opt_20', content: '...rest', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:40:00'
  },
  {
    id: 'q_b6c7d8e9',
    topicId: 'topic_py_funcs',
    content: 'Hàm generator trong Python sử dụng từ khóa nào để tạm ngưng và trả về giá trị từng bước?',
    difficulty: 'kho',
    options: [
      { id: 'opt_21', content: 'return', isCorrect: false },
      { id: 'opt_22', content: 'yield', isCorrect: true },
      { id: 'opt_23', content: 'pause', isCorrect: false },
      { id: 'opt_24', content: 'stop', isCorrect: false }
    ],
    createdAt: '2026-10-15T08:45:00'
  },
  {
    id: 'q_f0123456',
    topicId: 'topic_db_model',
    content: 'Khóa chính (Primary Key) trong mô hình quan hệ phải thỏa mãn điều kiện gì?',
    difficulty: 'de',
    options: [
      { id: 'opt_25', content: 'Duy nhất và không được chứa giá trị NULL', isCorrect: true },
      { id: 'opt_26', content: 'Được phép chứa tối đa một giá trị NULL', isCorrect: false },
      { id: 'opt_27', content: 'Chỉ được áp dụng cho cột có kiểu số nguyên', isCorrect: false },
      { id: 'opt_28', content: 'Bắt buộc phải tham chiếu đến một bảng khác', isCorrect: false }
    ],
    createdAt: '2026-10-16T09:45:00'
  },
  {
    id: 'q_789abcde',
    topicId: 'topic_db_sql',
    content: 'Mệnh đề nào trong SQL dùng để lọc các nhóm sau khi đã thực hiện gom nhóm GROUP BY?',
    difficulty: 'kho',
    options: [
      { id: 'opt_29', content: 'WHERE', isCorrect: false },
      { id: 'opt_30', content: 'HAVING', isCorrect: true },
      { id: 'opt_31', content: 'ORDER BY', isCorrect: false },
      { id: 'opt_32', content: 'FILTER', isCorrect: false }
    ],
    createdAt: '2026-10-16T09:50:00'
  },
  {
    id: 'q_f1e2d3c4',
    topicId: 'topic_net_osi',
    content: 'Tầng nào trong mô hình OSI chịu trách nhiệm chuyển tiếp gói tin giữa các mạng khác nhau (routing)?',
    difficulty: 'de',
    options: [
      { id: 'opt_33', content: 'Tầng mạng (Network Layer - Tầng 3)', isCorrect: true },
      { id: 'opt_34', content: 'Tầng liên kết dữ liệu (Data Link Layer - Tầng 2)', isCorrect: false },
      { id: 'opt_35', content: 'Tầng giao vận (Transport Layer - Tầng 4)', isCorrect: false },
      { id: 'opt_36', content: 'Tầng vật lý (Physical Layer - Tầng 1)', isCorrect: false }
    ],
    createdAt: '2026-10-18T10:25:00'
  }
];

export const INITIAL_USERS: User[] = [
  {
    id: 'user_admin_01',
    username: 'admin',
    email: 'admin@school.edu.vn',
    role: 'admin',
    salt: '8f7d9a1c2b3e4f50',
    passwordHash: '8a61421f6460e658760086c8a77f2d5ee16ffbbfd6d03f0b2f5c76c11707d8d2',
    createdAt: '2026-10-10T08:00:00'
  },
  {
    id: 'user_student_02',
    username: 'student',
    email: 'student@school.edu.vn',
    role: 'user',
    salt: '1a2b3c4d5e6f7081',
    passwordHash: '9b7253207571f769871197d9b8803e6ff2700cc0e7e1401c306d87d22818e9e3',
    createdAt: '2026-10-12T14:30:00'
  }
];

// Active exam containing question q_a1b2c3d4 for testing constraint check
export const INITIAL_EXAMS: Exam[] = [
  {
    id: 'exam_gk_python_01',
    subjectId: 'subj_py01',
    title: 'Đề kiểm tra giữa kỳ Python 2026',
    seed: 42,
    questionIds: ['q_a1b2c3d4', 'q_e5f60718', 'q_728394a5']
  }
];

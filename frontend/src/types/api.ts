export interface UserInfo {
  id: string
  username: string
  name: string | null
  status: string
  role_ids: string[]
  created_at: string
}

export interface MenuItem {
  id: string
  parent_id: string | null
  name: string
  path: string
  component: string
  icon: string | null
  sort: number
  visible: boolean
  permission_code: string | null
  children?: MenuItem[]
}

export interface RoleInfo {
  id: string
  name: string
  code: string
  description: string | null
  menu_ids: string[]
  button_ids: string[]
  created_at: string
}

export interface ButtonInfo {
  id: string
  menu_id: string
  name: string
  code: string
  description: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
  menus: MenuItem[]
  permissions: string[]
}

export interface ListResponse<T> {
  items: T[]
  total?: number
}

export interface DriverInfo {
  id: string
  name: string
  phone: string
  id_card: string | null
  license_no: string | null
  status: string
  rating: number
  hired_at: string | null
  created_at: string
  updated_at: string
}

export interface VehicleInfo {
  id: string
  plate_no: string
  brand: string
  model: string
  color: string | null
  status: string
  seat_count: number
  driver_id: string | null
  driver_name: string | null
  registered_at: string | null
  created_at: string
  updated_at: string
}

export interface ConversationInfo {
  id: string
  title: string
  thread_id: string
  agent_type: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant'
  content: string
  status_content?: string
  image_url?: string | null
  created_at?: string
}

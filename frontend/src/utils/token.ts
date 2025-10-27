const TOKEN_KEY = 'ai_prompt_lab_token'
const USER_KEY = 'ai_prompt_lab_user'

export const tokenStorage = {
  // 保存 token
  setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token)
  },

  // 获取 token
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  // 删除 token
  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
  },

  // 保存用户信息
  setUser(user: any) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  // 获取用户信息
  getUser(): any | null {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },

  // 删除用户信息
  removeUser() {
    localStorage.removeItem(USER_KEY)
  },

  // 清除所有
  clear() {
    this.removeToken()
    this.removeUser()
  }
}


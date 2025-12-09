import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'
import 'github-markdown-css/github-markdown-light.css'

// 配置 marked 的渲染器
const renderer = new marked.Renderer()

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  renderer: renderer
})

// 自定义代码高亮
marked.use({
  renderer: {
    code(code: string, language: string | undefined) {
      if (language && hljs.getLanguage(language)) {
        try {
          const highlighted = hljs.highlight(code, { language }).value
          return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
        } catch (err) {
          console.error('highlight error:', err)
        }
      }
      const highlighted = hljs.highlightAuto(code).value
      return `<pre><code class="hljs">${highlighted}</code></pre>`
    }
  }
})

/**
 * 渲染 Markdown
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''
  
  try {
    return marked(content) as string
  } catch (error) {
    console.error('Markdown render error:', error)
    return content
  }
}

/**
 * 变量信息接口
 */
export interface VariableInfo {
  name: string           // 变量名
  type: 'text' | 'textarea' | 'number' | 'select' | 'file'  // 类型
  defaultValue: string   // 默认值
  options: string[]      // 选项（仅 select 类型）
  required: boolean      // 是否必填
  placeholder: string    // 占位符
}

/**
 * 提取 Prompt 中的变量（简单版本，返回变量名数组）
 */
export function extractVariables(content: string): string[] {
  if (!content) return []
  
  const regex = /\{\{([^}]+)\}\}/g
  const variables: string[] = []
  let match

  while ((match = regex.exec(content)) !== null) {
    const varContent = match[1].trim()
    // 只取变量名部分（冒号前的内容）
    const varName = varContent.split(':')[0].trim()
    if (!variables.includes(varName)) {
      variables.push(varName)
    }
  }

  return variables
}

/**
 * 提取 Prompt 中的变量（增强版本，返回完整变量信息）
 * 
 * 支持格式：
 * - {{变量名}} - 简单文本变量
 * - {{变量名:类型}} - 指定类型
 * - {{变量名:类型:默认值}} - 指定默认值
 * - {{变量名:select:默认值:选项1,选项2,选项3}} - 下拉选择
 * - {{变量名:text:默认值:*}} - 必填标记
 */
export function extractVariablesEnhanced(content: string): VariableInfo[] {
  if (!content) return []
  
  const regex = /\{\{([^}]+)\}\}/g
  const variables: VariableInfo[] = []
  const seenNames = new Set<string>()
  let match

  while ((match = regex.exec(content)) !== null) {
    const varContent = match[1].trim()
    const parts = varContent.split(':').map(p => p.trim())
    
    const name = parts[0]
    if (seenNames.has(name)) continue
    seenNames.add(name)
    
    // 解析类型
    let type: VariableInfo['type'] = 'text'
    if (parts[1]) {
      const typeStr = parts[1].toLowerCase()
      if (['text', 'textarea', 'number', 'select', 'file'].includes(typeStr)) {
        type = typeStr as VariableInfo['type']
      }
    }
    
    // 解析默认值
    const defaultValue = parts[2] || ''
    
    // 解析选项或必填标记
    let options: string[] = []
    let required = false
    if (parts[3]) {
      if (parts[3] === '*') {
        required = true
      } else if (type === 'select') {
        options = parts[3].split(',').map(o => o.trim()).filter(Boolean)
      }
    }
    
    // 如果是 select 类型但没有选项，检查默认值部分是否包含选项
    if (type === 'select' && options.length === 0 && parts[2]?.includes(',')) {
      options = parts[2].split(',').map(o => o.trim()).filter(Boolean)
    }
    
    variables.push({
      name,
      type,
      defaultValue: type === 'select' && options.length > 0 ? options[0] : defaultValue,
      options,
      required,
      placeholder: `请输入${name}`
    })
  }

  return variables
}

/**
 * 替换变量预览（支持增强格式）
 */
export function previewWithVariables(
  content: string, 
  variables: Record<string, string>
): string {
  if (!content) return ''
  
  let result = content
  
  for (const [key, value] of Object.entries(variables)) {
    // 匹配简单格式和增强格式
    const regex = new RegExp(`\\{\\{\\s*${key}(?::[^}]*)?\\s*\\}\\}`, 'g')
    result = result.replace(regex, value || `{{${key}}}`)
  }
  
  return result
}

/**
 * 高亮变量语法
 */
export function highlightVariables(content: string): string {
  if (!content) return ''
  
  return content.replace(
    /\{\{([^}]+)\}\}/g, 
    '<span class="text-primary font-semibold">${{$1}}</span>'
  )
}


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
 * 提取 Prompt 中的变量
 */
export function extractVariables(content: string): string[] {
  if (!content) return []
  
  const regex = /\{\{([^}]+)\}\}/g
  const variables: string[] = []
  let match

  while ((match = regex.exec(content)) !== null) {
    const varName = match[1].trim()
    if (!variables.includes(varName)) {
      variables.push(varName)
    }
  }

  return variables
}

/**
 * 替换变量预览
 */
export function previewWithVariables(
  content: string, 
  variables: Record<string, string>
): string {
  if (!content) return ''
  
  let result = content
  
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g')
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


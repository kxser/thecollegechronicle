import { consola } from 'consola'

declare global {
  // Extend the Console interface so TypeScript knows about console.box
  interface Console {
    box?: (message: string) => void
  }
}

if (typeof console.box !== 'function') {
  console.box = (message: string) => {
    consola.box(message)
  }
}

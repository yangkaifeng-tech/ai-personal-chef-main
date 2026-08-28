import type { Directive } from 'vue'
import { useAuthStore } from '../stores/auth'

export const permissionDirective: Directive<HTMLElement, string> = {
  mounted(element, binding) {
    const authStore = useAuthStore()
    if (binding.value && !authStore.hasPermission(binding.value)) {
      element.remove()
    }
  },
}

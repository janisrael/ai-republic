<template>
  <span 
    :class="iconClasses" 
    :style="iconStyles"
    v-bind="$attrs"
  >
    {{ iconName }}
  </span>
</template>

<script>
export default {
  name: 'Icon',
  inheritAttrs: false,
  props: {
    name: {
      type: String,
      required: true,
      validator: (value) => {
        // Common Material Icons for AI Dashboard
        const validIcons = [
          // Navigation & UI
          'home', 'dashboard', 'menu', 'close', 'arrow_back', 'arrow_forward',
          'expand_more', 'expand_less', 'more_vert', 'more_horiz',
          
          // Actions
          'play_arrow', 'pause', 'stop', 'refresh', 'restart_alt',
          'upload', 'download', 'save', 'edit', 'delete', 'add', 'remove',
          'search', 'filter_list', 'sort', 'settings', 'tune',
          
          // AI & ML
          'psychology', 'smart_toy', 'auto_awesome', 'memory',
          'model_training', 'precision_manufacturing', 'biotech',
          'science', 'analytics', 'trending_up', 'insights',
          
          // Data & Files
          'folder', 'folder_open', 'description', 'data_object',
          'storage', 'cloud_upload', 'cloud_download', 'cloud_sync',
          'dataset', 'table_chart', 'bar_chart', 'pie_chart',
          
          // Status & Feedback
          'check_circle', 'error', 'warning', 'info', 'help',
          'done', 'pending', 'schedule', 'timer', 'alarm',
          'notifications', 'notifications_active', 'notifications_off',
          
          // Communication
          'chat', 'message', 'email', 'phone', 'video_call',
          'share', 'link', 'content_copy', 'visibility', 'visibility_off',
          
          // System & Security
          'security', 'lock', 'lock_open', 'verified_user',
          'admin_panel_settings', 'person', 'group', 'account_circle',
          
          // Development
          'code', 'terminal', 'bug_report', 'build', 'deploy',
          'rocket_launch', 'assessment', 'speed', 'memory',
          
          // Media
          'image', 'video_file', 'audio_file', 'text_snippet',
          'attach_file', 'insert_drive_file', 'picture_as_pdf',
          
          // Time & Calendar
          'schedule', 'event', 'calendar_today', 'access_time',
          'history', 'update', 'sync', 'autorenew',

          'eye_tracking'
        ];
        return validIcons.includes(value);
      }
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'].includes(value)
    },
    color: {
      type: String,
      default: '',
      validator: (value) => ['', 'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark', 'muted'].includes(value)
    },
    spin: {
      type: Boolean,
      default: false
    },
    hover: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    iconName() {
      return this.name;
    },
    iconClasses() {
      const classes = ['material-icons-round'];
      
      // Size class
      if (this.size !== 'md') {
        classes.push(`icon-${this.size}`);
      }
      
      // Color class
      if (this.color) {
        classes.push(`icon-${this.color}`);
      }
      
      // State classes
      if (this.spin) {
        classes.push('icon-spin');
      }
      
      if (this.hover) {
        classes.push('icon-hover');
      }
      
      return classes;
    },
    iconStyles() {
      return {};
    }
  }
}
</script>

<style scoped>
.material-icons-round {
  user-select: none;
}
</style>

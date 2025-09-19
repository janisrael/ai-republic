<template>
  <div class="ai-room-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>🤖 AI Room</h1>
        <p>Multi-agent conversation simulation and data collection</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="clearConversation" :disabled="isRunning">
          <Icon name="clear" size="sm" color="light" />
          Clear Chat
        </button>
        <button class="btn btn-primary" @click="toggleConversation" :disabled="!selectedAgents.length">
          <Icon :name="isRunning ? 'pause' : 'play_arrow'" size="sm" color="light" />
          {{ isRunning ? 'Stop' : 'Start' }} Conversation
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="smart_toy" size="lg" color="primary" />
        </div>
        <div class="card-content">
          <h3>{{ availableAgents.length }}</h3>
          <p>Available Agents</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="group" size="lg" color="success" />
        </div>
        <div class="card-content">
          <h3>{{ selectedAgents.length }}</h3>
          <p>Active Agents</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="chat" size="lg" color="info" />
        </div>
        <div class="card-content">
          <h3>{{ conversationHistory.length }}</h3>
          <p>Messages</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="schedule" size="lg" color="warning" />
        </div>
        <div class="card-content">
          <h3>{{ conversationDuration }}</h3>
          <p>Duration</p>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="dashboard-grid">
      <!-- Agent Selection Panel -->
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>🎯 Agent Selection</h3>
            <p>Choose which AI agents participate in the conversation</p>
          </div>
          <div class="card-body">
            <div class="agent-selection">
              <div class="selection-controls">
                <button class="btn btn-sm btn-secondary" @click="selectAllAgents">
                  Select All
                </button>
                <button class="btn btn-sm btn-secondary" @click="clearSelection">
                  Clear All
                </button>
              </div>
              
              <div class="agents-grid">
                <div 
                  v-for="agent in availableAgents" 
                  :key="agent.name"
                  class="agent-card"
                  :class="{ 'selected': selectedAgents.includes(agent.name) }"
                  @click="toggleAgentSelection(agent.name)"
                >
                  <div class="agent-avatar">
                    <img v-if="agent.avatar_url" :src="agent.avatar_url" :alt="agent.name + ' avatar'" class="avatar-image">
                    <div v-else class="avatar-placeholder">
                      <span class="material-icons-round">smart_toy</span>
                    </div>
                  </div>
                  <div class="agent-info">
                    <h4>{{ agent.name }}</h4>
                    <p class="agent-capabilities">{{ agent.capabilities?.join(', ') || 'General Purpose' }}</p>
                    <div class="agent-stats">
                      <span class="stat">{{ agent.parameters || 'N/A' }}</span>
                      <span class="stat">{{ agent.context_length || 'N/A' }}</span>
                      <span class="stat" :class="getModelSpeedClass(agent.name)">
                        {{ getModelSpeed(agent.name) }}
                      </span>
                    </div>
                  </div>
                  <div class="selection-indicator">
                    <span class="material-icons-round">
                      {{ selectedAgents.includes(agent.name) ? 'check_circle' : 'radio_button_unchecked' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Conversation Settings -->
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>⚙️ Conversation Settings</h3>
            <p>Configure the conversation parameters</p>
          </div>
          <div class="card-body">
            <div class="settings-grid">
              <div class="form-group">
                <label>Max Messages</label>
                <input 
                  type="number" 
                  v-model="settings.maxMessages" 
                  min="10" 
                  max="1000" 
                  class="form-control"
                >
                <small>Maximum number of messages in the conversation</small>
              </div>
              
              <div class="form-group">
                <label>Message Delay (seconds)</label>
                <input 
                  type="number" 
                  v-model="settings.messageDelay" 
                  min="1" 
                  max="30" 
                  class="form-control"
                >
                <small>Delay between messages for readability</small>
              </div>
              
              <div class="form-group">
                <label>Conversation Topic</label>
                <select v-model="settings.topic" class="form-control">
                  <option value="random">Random Topics</option>
                  <option value="custom">Custom Topic</option>
                  <option value="technology">Technology</option>
                  <option value="science">Science</option>
                  <option value="philosophy">Philosophy</option>
                  <option value="creative">Creative Writing</option>
                  <option value="problem-solving">Problem Solving</option>
                </select>
                <small>Choose the conversation theme</small>
              </div>
              
              <div v-if="settings.topic === 'custom'" class="custom-topic-section">
                <div class="form-group">
                  <label>Topic Title</label>
                  <input 
                    type="text" 
                    v-model="customTopic.title" 
                    class="form-control" 
                    placeholder="e.g., Future of AI, Climate Change Solutions"
                  >
                </div>
                
                <div class="form-group">
                  <label>Topic Description</label>
                  <textarea 
                    v-model="customTopic.description" 
                    class="form-control" 
                    rows="2"
                    placeholder="Describe what you want the AI models to discuss..."
                  ></textarea>
                </div>
                
                <div class="form-group">
                  <label>Category</label>
                  <select v-model="customTopic.category" class="form-control">
                    <option value="technology">Technology</option>
                    <option value="science">Science</option>
                    <option value="philosophy">Philosophy</option>
                    <option value="business">Business</option>
                    <option value="creative">Creative</option>
                    <option value="education">Education</option>
                    <option value="health">Health</option>
                    <option value="environment">Environment</option>
                    <option value="social">Social Issues</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                
                <div class="topic-actions">
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="generateTopicPrompt"
                    :disabled="!customTopic.title.trim()"
                  >
                    <span class="material-icons-round">auto_awesome</span>
                    Generate
                  </button>
                  
                  <button 
                    class="btn btn-sm btn-secondary" 
                    @click="clearCustomTopic"
                  >
                    <span class="material-icons-round">clear</span>
                    Clear
                  </button>
                </div>
                
                <!-- Generated Prompt Display -->
                <div v-if="generatedPrompt" class="generated-prompt">
                  <h5>Generated Conversation Starter:</h5>
                  <div class="prompt-content">
                    <p>{{ generatedPrompt }}</p>
                  </div>
                  <div class="prompt-actions">
                    <button class="btn btn-sm btn-success" @click="copyPrompt">
                      <span class="material-icons-round">content_copy</span>
                      Copy
                    </button>
                    <button class="btn btn-sm btn-info" @click="useGeneratedPrompt">
                      <span class="material-icons-round">check</span>
                      Use This
                    </button>
                  </div>
                </div>
                
                <!-- Manual Input -->
                <div class="form-group">
                  <label>Or Enter Manually</label>
                  <textarea 
                    v-model="settings.customTopic" 
                    class="form-control" 
                    placeholder="Enter your custom conversation starter..."
                    rows="3"
                  ></textarea>
                  <small>This will be the first message in the conversation</small>
                </div>
              </div>
              
              <div class="form-group">
                <label>Temperature</label>
                <input 
                  type="range" 
                  v-model="settings.temperature" 
                  min="0.1" 
                  max="2.0" 
                  step="0.1" 
                  class="form-control"
                >
                <small>Creativity level: {{ settings.temperature }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Display -->
    <div class="chatroom-section">
      <div class="neumorphic-card">
        <div class="card-header">
          <h3>💬 AI Conversation</h3>
          <div class="conversation-controls">
            <span class="status-indicator" :class="{ 'active': isRunning, 'generating': isGeneratingResponse }">
              {{ isGeneratingResponse ? '🤔 Generating...' : (isRunning ? '🟢 Active' : '🔴 Stopped') }}
            </span>
            <button class="btn btn-sm btn-secondary" @click="exportConversation">
              <Icon name="download" size="xs" color="light" />
              Export
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="chatroom-display" ref="chatroomDisplay">
            <div v-if="conversationHistory.length === 0" class="empty-conversation">
              <div class="empty-icon">🤖</div>
              <h3>No conversation yet</h3>
              <p>Select agents and start the conversation to see AI agents chat with each other!</p>
            </div>
            
            <div 
              v-for="message in conversationHistory" 
              :key="message.id" 
              class="message-item"
              :style="{ '--agent-color': getAgentColor(message.agent) }"
            >
              <div class="message-avatar">
                <img v-if="getAgentAvatar(message.agent)" :src="getAgentAvatar(message.agent)" :alt="message.agent + ' avatar'" class="avatar-image">
                <div v-else class="avatar-placeholder">
                  <span class="material-icons-round">smart_toy</span>
                </div>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="agent-name">{{ message.agent }}</span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-text">{{ message.text }}</div>
              </div>
            </div>
            
            <div v-if="isGeneratingResponse" class="typing-indicator">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span>AI agent is thinking...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Icon from '../components/Icon.vue';

export default {
  name: 'AIRoomView',
  components: {
    Icon
  },
  data() {
    return {
      availableAgents: [],
      selectedAgents: [],
      conversationHistory: [],
      isRunning: false,
      conversationStartTime: null,
      conversationTimer: null,
      messageIdCounter: 0,
      isGeneratingResponse: false,
      agentTimeoutCount: {},
      settings: {
        maxMessages: 50,
        messageDelay: 3,
        topic: 'random',
        customTopic: '',
        temperature: 0.7
      },
      customTopic: {
        title: '',
        description: '',
        category: 'technology'
      },
      generatedPrompt: '',
      conversationTopics: {
        random: [
          "Hello everyone! How's your day going?",
          "Let's discuss something interesting today!",
          "What's on your mind today?",
          "I have a question for all of you...",
          "Let's talk about the future!"
        ],
        technology: [
          "What do you think about the latest AI developments?",
          "How will technology change our lives in the next decade?",
          "Let's discuss the pros and cons of automation.",
          "What's your take on quantum computing?",
          "How important is cybersecurity in our digital world?"
        ],
        science: [
          "What's the most fascinating scientific discovery you know?",
          "Let's talk about space exploration!",
          "How do you think climate change will affect our planet?",
          "What's your opinion on genetic engineering?",
          "Let's discuss the mysteries of the universe!"
        ],
        philosophy: [
          "What does it mean to be conscious?",
          "Is there such a thing as objective truth?",
          "What's the purpose of human existence?",
          "How do we define good and evil?",
          "What is the nature of reality?"
        ],
        creative: [
          "Let's write a story together!",
          "What's the most creative thing you can imagine?",
          "Let's brainstorm ideas for a novel.",
          "How would you describe beauty?",
          "Let's create something amazing together!"
        ],
        'problem-solving': [
          "Let's solve a complex problem together.",
          "What's the best approach to tackle challenges?",
          "How do you prioritize when everything seems urgent?",
          "Let's think outside the box for a moment.",
          "What's your problem-solving methodology?"
        ]
      }
    };
  },
  computed: {
    conversationDuration() {
      if (!this.conversationStartTime) return '0:00';
      const elapsed = Date.now() - this.conversationStartTime;
      const minutes = Math.floor(elapsed / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
  },
  mounted() {
    this.loadAvailableAgents();
    this.checkForCustomTopic();
  },
  beforeUnmount() {
    this.stopConversation();
  },
  methods: {
    async loadAvailableAgents() {
      try {
        const response = await fetch('http://localhost:5000/api/models');
        const result = await response.json();
        
        if (result.success) {
          this.availableAgents = result.models.map(model => ({
            name: model.name,
            capabilities: model.capabilities || ['General Purpose'],
            parameters: model.parameters,
            context_length: model.context_length,
            avatar_url: model.avatar_url
          }));
        }
      } catch (error) {
        console.error('Error loading agents:', error);
      }
    },
    
    checkForCustomTopic() {
      // Check if there's a custom topic from Dashboard
      const customTopic = localStorage.getItem('customTopic');
      if (customTopic) {
        this.settings.topic = 'custom';
        this.settings.customTopic = customTopic;
        // Clear the stored topic so it doesn't persist
        localStorage.removeItem('customTopic');
        
        // Show a notification
        alert('Custom topic loaded from Dashboard! You can now start the conversation.');
      }
    },
    
    generateTopicPrompt() {
      if (!this.customTopic.title.trim()) {
        alert('Please enter a topic title');
        return;
      }
      
      const categoryPrompts = {
        technology: 'Let\'s discuss the latest developments and future implications',
        science: 'Let\'s explore the scientific aspects and research findings',
        philosophy: 'Let\'s dive into the deeper philosophical implications',
        business: 'Let\'s analyze the business and economic perspectives',
        creative: 'Let\'s explore creative and innovative approaches',
        education: 'Let\'s discuss educational implications and learning opportunities',
        health: 'Let\'s examine health and wellness considerations',
        environment: 'Let\'s explore environmental impact and sustainability',
        social: 'Let\'s discuss social implications and community perspectives',
        other: 'Let\'s explore this topic from multiple angles'
      };
      
      const categoryPrompt = categoryPrompts[this.customTopic.category] || categoryPrompts.other;
      
      this.generatedPrompt = `${this.customTopic.title}

${this.customTopic.description ? this.customTopic.description + '\n\n' : ''}${categoryPrompt}. Share your thoughts, insights, and perspectives on this topic. What are the key challenges, opportunities, and potential solutions?`;
    },
    
    clearCustomTopic() {
      this.customTopic = {
        title: '',
        description: '',
        category: 'technology'
      };
      this.generatedPrompt = '';
    },
    
    async copyPrompt() {
      try {
        await navigator.clipboard.writeText(this.generatedPrompt);
        alert('Prompt copied to clipboard!');
      } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = this.generatedPrompt;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Prompt copied to clipboard!');
      }
    },
    
    useGeneratedPrompt() {
      this.settings.customTopic = this.generatedPrompt;
      this.generatedPrompt = '';
    },
    
    toggleAgentSelection(agentName) {
      const index = this.selectedAgents.indexOf(agentName);
      if (index > -1) {
        this.selectedAgents.splice(index, 1);
      } else {
        this.selectedAgents.push(agentName);
      }
    },
    
    selectAllAgents() {
      this.selectedAgents = this.availableAgents.map(agent => agent.name);
    },
    
    clearSelection() {
      this.selectedAgents = [];
    },
    
    toggleConversation() {
      if (this.isRunning) {
        this.stopConversation();
      } else {
        this.startConversation();
      }
    },
    
    startConversation() {
      if (this.selectedAgents.length === 0) {
        alert('Please select at least one agent to start the conversation.');
        return;
      }
      
      if (this.settings.topic === 'custom' && !this.settings.customTopic.trim()) {
        alert('Please enter a custom topic to start the conversation');
        return;
      }
      
      this.isRunning = true;
      this.conversationStartTime = Date.now();
      this.agentTimeoutCount = {}; // Reset timeout counts
      this.startConversationTimer();
      
      // Start with a random message from the first agent
      this.initiateConversation();
    },
    
    stopConversation() {
      this.isRunning = false;
      this.isGeneratingResponse = false;
      if (this.conversationTimer) {
        clearInterval(this.conversationTimer);
        this.conversationTimer = null;
      }
    },
    
    initiateConversation() {
      let firstMessage;
      
      if (this.settings.topic === 'custom' && this.settings.customTopic.trim()) {
        // Use custom topic if provided
        firstMessage = this.settings.customTopic.trim();
      } else {
        // Use predefined topics
        const topics = this.conversationTopics[this.settings.topic] || this.conversationTopics.random;
        firstMessage = topics[Math.floor(Math.random() * topics.length)];
      }
      
      const firstAgent = this.selectedAgents[0];
      this.addMessage(firstAgent, firstMessage);
      
      // Start the conversation loop
      this.conversationTimer = setInterval(() => {
        this.generateNextMessage();
      }, this.settings.messageDelay * 1000);
    },
    
    async generateNextMessage() {
      if (!this.isRunning || this.conversationHistory.length >= this.settings.maxMessages) {
        this.stopConversation();
        return;
      }
      
      // Don't start new message if one is already being generated
      if (this.isGeneratingResponse) {
        return;
      }
      
      // Select a random agent (excluding the last speaker and agents with too many timeouts)
      const lastMessage = this.conversationHistory[this.conversationHistory.length - 1];
      const availableAgents = this.selectedAgents.filter(agent => {
        return agent !== lastMessage.agent && (this.agentTimeoutCount[agent] || 0) < 3;
      });
      
      if (availableAgents.length === 0) {
        console.log('No available agents, stopping conversation');
        this.stopConversation();
        return;
      }
      
      const nextAgent = availableAgents[Math.floor(Math.random() * availableAgents.length)];
      
      // Generate response based on conversation context
      await this.generateAgentResponse(nextAgent);
    },
    
    async generateAgentResponse(agentName) {
      // Set flag to prevent multiple simultaneous requests
      this.isGeneratingResponse = true;
      
      try {
        // Get the last few messages for context
        const recentMessages = this.conversationHistory.slice(-3);
        const context = recentMessages.map(msg => `${msg.agent}: ${msg.text}`).join('\n');
        
        // Create a prompt for the agent
        const prompt = `You are ${agentName}, an AI assistant participating in a group conversation. Here's the recent conversation:\n\n${context}\n\nRespond naturally and continue the discussion. If someone asked a question, try to answer it. If someone made a point, build on it or offer a different perspective. Keep your response conversational, helpful, and engaging. Don't repeat timeout messages or error responses.`;
        
        console.log(`🤖 Generating response for ${agentName}...`);
        
        // Call the Ollama API with timeout (longer for large models)
        const controller = new AbortController();
        const timeoutDuration = agentName.includes('12B') || agentName.includes('13B') ? 120000 : 60000; // 2 min for large models, 1 min for others
        const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);
        
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: agentName,
            prompt: prompt,
            stream: false,
            options: {
              temperature: this.settings.temperature,
              top_p: 0.9
            }
          }),
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const responseText = result.response || 'I need a moment to think about that...';
        
        console.log(`✅ Response received from ${agentName}`);
        this.addMessage(agentName, responseText);
        
      } catch (error) {
        console.error('Error generating agent response:', error);
        
        if (error.name === 'AbortError') {
          // Track timeout count for this agent
          this.agentTimeoutCount[agentName] = (this.agentTimeoutCount[agentName] || 0) + 1;
          
          const isLargeModel = agentName.includes('12B') || agentName.includes('13B');
          const timeoutMsg = isLargeModel 
            ? 'I need more time to think about this complex topic...' 
            : 'Let me think about that for a moment...';
          this.addMessage(agentName, timeoutMsg);
          
          console.log(`⚠️ Agent ${agentName} timeout count: ${this.agentTimeoutCount[agentName]}`);
        } else if (error.message.includes('404')) {
          this.addMessage(agentName, 'I\'m having trouble accessing my knowledge base right now.');
        } else {
          this.addMessage(agentName, 'That\'s an interesting point. Could you elaborate?');
        }
      } finally {
        // Always clear the flag when done
        this.isGeneratingResponse = false;
      }
    },
    
    addMessage(agent, text) {
      const message = {
        id: ++this.messageIdCounter,
        agent: agent,
        text: text,
        timestamp: new Date()
      };
      
      this.conversationHistory.push(message);
      this.scrollToBottom();
    },
    
    clearConversation() {
      this.conversationHistory = [];
      this.messageIdCounter = 0;
      this.stopConversation();
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const chatroom = this.$refs.chatroomDisplay;
        if (chatroom) {
          chatroom.scrollTop = chatroom.scrollHeight;
        }
      });
    },
    
    getAgentAvatar(agentName) {
      const agent = this.availableAgents.find(a => a.name === agentName);
      return agent?.avatar_url;
    },
    
    getAgentColor(agentName) {
      // Define colors for different agents
      const colors = {
        'testevaluation:v1.0': '#10B981', // Green
        'salamanka:latest': '#3B82F6',   // Blue
        'r22:latest': '#F59E0B',          // Orange
        'bandila:latest': '#8B5CF6',      // Purple
        'bandilarag:latest': '#EF4444',   // Red
        'r1:latest': '#06B6D4',          // Cyan
        'r2:latest': '#84CC16',          // Lime
        'r3:latest': '#F97316',          // Orange Red
        'r4:latest': '#EC4899',          // Pink
        'r5:latest': '#6366F1',          // Indigo
      };
      
      return colors[agentName] || '#6B7280'; // Default gray
    },
    
    getModelSpeed(agentName) {
      // Determine model speed based on size indicators
      if (agentName.includes('12B') || agentName.includes('13B')) {
        return '🐌 Slow';
      } else if (agentName.includes('7B') || agentName.includes('8B')) {
        return '⚡ Fast';
      } else if (agentName.includes('3B') || agentName.includes('4B')) {
        return '🚀 Very Fast';
      } else {
        return '⚡ Fast';
      }
    },
    
    getModelSpeedClass(agentName) {
      // Return CSS class for speed indicator
      if (agentName.includes('12B') || agentName.includes('13B')) {
        return 'speed-slow';
      } else if (agentName.includes('7B') || agentName.includes('8B')) {
        return 'speed-fast';
      } else if (agentName.includes('3B') || agentName.includes('4B')) {
        return 'speed-very-fast';
      } else {
        return 'speed-fast';
      }
    },
    
    formatTime(timestamp) {
      return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    exportConversation() {
      const data = {
        timestamp: new Date().toISOString(),
        agents: this.selectedAgents,
        settings: this.settings,
        conversation: this.conversationHistory.map(msg => ({
          agent: msg.agent,
          text: msg.text,
          timestamp: msg.timestamp.toISOString()
        }))
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai-conversation-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    startConversationTimer() {
      setInterval(() => {
        // Timer updates are handled by the computed property
      }, 1000);
    }
  }
};
</script>

<style scoped>
.ai-room-container {
  padding: 2rem;
  /* max-width: 1400px; */
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.page-header p {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: var(--transition);
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius);
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.card-content p {
  color: var(--text-muted);
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.dashboard-col {
  display: flex;
  flex-direction: column;
}

.neumorphic-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: var(--transition);
}

.neumorphic-card:hover {
  box-shadow: var(--shadow-hover);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.card-header p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.9rem;
}

.card-body {
  padding: 1.5rem;
}

.agent-selection {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selection-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.agents-grid {
  display: grid;
  gap: 1rem;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--radius-sm);
  border: 2px solid transparent;
  cursor: pointer;
  transition: var(--transition);
  background: rgba(255, 255, 255, 0.5);
}

.agent-card:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-1px);
}

.agent-card.selected {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.1);
}

.agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-info {
  flex: 1;
}

.agent-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.agent-capabilities {
  margin: 0 0 0.5rem 0;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.agent-stats {
  display: flex;
  gap: 0.5rem;
}

.stat {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.speed-slow {
  color: #EF4444 !important;
  font-weight: 600;
}

.speed-fast {
  color: #10B981 !important;
  font-weight: 600;
}

.speed-very-fast {
  color: #3B82F6 !important;
  font-weight: 600;
}

.selection-indicator {
  color: var(--primary);
}

.settings-grid {
  display: grid;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.form-control {
  padding: 0.75rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  transition: var(--transition);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
}

.form-group small {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.chatroom-section {
  margin-top: 2rem;
}

.conversation-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-indicator {
  font-size: 0.9rem;
  font-weight: 600;
}

.status-indicator.active {
  color: var(--success);
}

.status-indicator.generating {
  color: var(--warning);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Custom Topic Styles */
.custom-topic-section {
  background: #f8f9fc;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 0.5rem;
}

.custom-topic-section .form-group {
  margin-bottom: 1rem;
}

.custom-topic-section .form-group:last-child {
  margin-bottom: 0;
}

.custom-topic-section label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
  display: block;
}

.custom-topic-section .form-control {
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.85rem;
  transition: border-color 0.3s ease;
}

.custom-topic-section .form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(78, 115, 223, 0.1);
}

.topic-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.topic-actions .btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.topic-actions .btn-primary {
  background: var(--primary-color);
  color: white;
}

.topic-actions .btn-primary:hover:not(:disabled) {
  background: #3d5fd9;
  transform: translateY(-1px);
}

.topic-actions .btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.topic-actions .btn-secondary {
  background: #f8f9fc;
  color: var(--text-color);
  border: 1px solid #e0e0e0;
}

.topic-actions .btn-secondary:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.generated-prompt {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.generated-prompt h5 {
  margin: 0 0 0.75rem 0;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 600;
}

.prompt-content {
  background: #f8f9fc;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 0.85rem;
}

.prompt-content p {
  margin: 0;
  color: var(--text-color);
}

.prompt-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
}

.prompt-actions .btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.prompt-actions .btn-success {
  background: var(--success-color);
  color: white;
}

.prompt-actions .btn-success:hover {
  background: #17a673;
  transform: translateY(-1px);
}

.prompt-actions .btn-info {
  background: var(--info-color);
  color: white;
}

.prompt-actions .btn-info:hover {
  background: #2a9bb8;
  transform: translateY(-1px);
}

.chatroom-display {
    max-height: 1600px;
  overflow-y: auto;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-sm);
}

.empty-conversation {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-conversation h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.empty-conversation p {
  margin: 0;
}

.message-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: var(--radius-sm);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid var(--agent-color, #6B7280);
  transition: all 0.3s ease;
}

.message-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.agent-name {
  font-weight: 600;
  color: var(--agent-color, var(--text-color));
  font-size: 0.9rem;
}

.message-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.message-text {
  color: var(--text-color);
  line-height: 1.5;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: var(--text-muted);
  font-style: italic;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--secondary);
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>

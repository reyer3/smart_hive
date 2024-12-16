# Frontend Development

## 1. Arquitectura Frontend

### 1.1. Tecnologías Base
- **Framework:** Qwik
- **Estado:** Señales y stores
- **Estilos:** Tailwind CSS
- **API Client:** tRPC

### 1.2. Estructura de Directorios
```plaintext
src/
  ├── components/
  │   ├── agents/
  │   ├── editor/
  │   ├── shared/
  │   └── workspace/
  ├── hooks/
  ├── routes/
  ├── stores/
  └── utils/
```

## 2. Componentes de Agente

### 2.1. AgentWorkspace
```typescript
interface AgentWorkspaceProps {
  activeAgent: Agent;
  context: WorkspaceContext;
  onTaskComplete: (result: TaskResult) => void;
}

export const AgentWorkspace = component$((props: AgentWorkspaceProps) => {
  const taskStore = useTaskStore();
  const preferences = usePreferences();

  return (
    <div class="flex flex-col h-full">
      <AgentHeader agent={props.activeAgent} />
      <AgentContent
        context={props.context}
        preferences={preferences}
      />
      <AgentToolbar
        onAction={handleAgentAction}
        tools={props.activeAgent.tools}
      />
    </div>
  );
});
```

### 2.2. AgentChat
```typescript
interface AgentChatProps {
  agent: Agent;
  messages: Message[];
  onSend: (message: string) => void;
}

export const AgentChat = component$((props: AgentChatProps) => {
  const messageStore = useMessageStore();
  
  return (
    <div class="flex flex-col h-full">
      <ChatHistory messages={props.messages} />
      <ChatInput
        onSend={props.onSend}
        suggestions={messageStore.suggestions}
      />
    </div>
  );
});
```

## 3. Editor Integration

### 3.1. CodeEditor
```typescript
interface CodeEditorProps {
  file: string;
  language: string;
  onChange: (content: string) => void;
  suggestions: CodeSuggestion[];
}

export const CodeEditor = component$((props: CodeEditorProps) => {
  const editorStore = useEditorStore();
  
  return (
    <div class="relative h-full">
      <MonacoEditor
        value={props.content}
        language={props.language}
        onChange={handleChange}
      />
      <SuggestionPanel
        suggestions={props.suggestions}
        onAccept={handleAcceptSuggestion}
      />
    </div>
  );
});
```

### 3.2. AgentAssist
```typescript
interface AgentAssistProps {
  activeFile: string;
  selectedText: string;
  onSuggestion: (suggestion: Suggestion) => void;
}

export const AgentAssist = component$((props: AgentAssistProps) => {
  const assistStore = useAssistStore();
  
  return (
    <div class="flex flex-col gap-2">
      <InlineSuggestions
        suggestions={assistStore.inlineSuggestions}
        onAccept={handleAcceptSuggestion}
      />
      <ActionPanel
        actions={assistStore.availableActions}
        onAction={handleAction}
      />
    </div>
  );
});
```

## 4. Gestión de Estado

### 4.1. Stores
```typescript
// Task Store
export const useTaskStore = createStore({
  tasks: [] as Task[],
  activeTask: null as Task | null,
  
  addTask: $((task: Task) => {
    // Implementación
  }),
  
  completeTask: $((taskId: string) => {
    // Implementación
  })
});

// Agent Store
export const useAgentStore = createStore({
  agents: [] as Agent[],
  activeAgent: null as Agent | null,
  
  selectAgent: $((agentId: string) => {
    // Implementación
  }),
  
  updateAgentState: $((agentId: string, state: AgentState) => {
    // Implementación
  })
});
```

### 4.2. Señales
```typescript
// Preferencias de Usuario
export const usePreferences = createSignal({
  theme: 'light',
  language: 'es',
  editorConfig: {
    fontSize: 14,
    tabSize: 2,
    // ...más configuraciones
  }
});

// Estado de Conexión
export const useConnection = createSignal({
  status: 'connected',
  latency: 0,
  lastSync: null as Date | null
});
```

## 5. Comunicación en Tiempo Real

### 5.1. WebSocket Client
```typescript
class AgentWebSocket {
  private ws: WebSocket;
  private messageQueue: Message[] = [];
  
  constructor(agentId: string) {
    this.ws = new WebSocket(`ws://api/agent/${agentId}`);
    this.setupHandlers();
  }
  
  private setupHandlers() {
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }
  
  public send(message: Message) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }
}
```

### 5.2. Event Bus
```typescript
export const eventBus = {
  listeners: new Map<string, Function[]>(),
  
  emit(event: string, data: any) {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach(listener => listener(data));
  },
  
  on(event: string, callback: Function) {
    const listeners = this.listeners.get(event) || [];
    listeners.push(callback);
    this.listeners.set(event, listeners);
  }
};
```

## 6. Personalización de UI

### 6.1. Temas
```typescript
export const themes = {
  light: {
    primary: '#1a73e8',
    secondary: '#ea4335',
    background: '#ffffff',
    text: '#202124'
  },
  dark: {
    primary: '#8ab4f8',
    secondary: '#81c995',
    background: '#202124',
    text: '#ffffff'
  }
};
```

### 6.2. Layouts
```typescript
export const WorkspaceLayout = component$(() => {
  const layout = useLayoutStore();
  
  return (
    <div class="grid grid-cols-12 h-screen">
      <Sidebar class="col-span-2" />
      <main class="col-span-7">
        <EditorPanel />
      </main>
      <aside class="col-span-3">
        <AgentPanel />
      </aside>
    </div>
  );
});
```

## 7. Optimización

### 7.1. Code Splitting
```typescript
// Lazy loading de componentes pesados
const AgentWorkspace = lazy$(() => import('./AgentWorkspace'));
const CodeEditor = lazy$(() => import('./CodeEditor'));
```

### 7.2. Caché
```typescript
export const useAgentCache = () => {
  const cache = new Map<string, AgentResponse>();
  
  return {
    get: (key: string) => cache.get(key),
    set: (key: string, value: AgentResponse) => {
      cache.set(key, value);
      setTimeout(() => cache.delete(key), 5 * 60 * 1000); // 5 min TTL
    }
  };
};
```

## 8. Testing

### 8.1. Componentes
```typescript
describe('AgentWorkspace', () => {
  test('renders active agent', async () => {
    const agent = mockAgent();
    const { getByText } = render(<AgentWorkspace agent={agent} />);
    expect(getByText(agent.name)).toBeInTheDocument();
  });
});
```

### 8.2. Integración
```typescript
describe('Agent Communication', () => {
  test('sends and receives messages', async () => {
    const ws = new AgentWebSocket('test-agent');
    const message = { type: 'TEST', content: 'Hello' };
    
    ws.send(message);
    const response = await waitForMessage(ws);
    expect(response.type).toBe('TEST_RESPONSE');
  });
});
export interface NavigationEntry {
  section: string;
  context: Record<string, any>;
}

export interface SessionState {
  userId: string;
  currentSection: string;
  context: Record<string, any>;
  navigationStack: NavigationEntry[];
}

const sessions = new Map<string, SessionState>();

export function getSession(userId: string): SessionState {
  if (!sessions.has(userId)) {
    sessions.set(userId, {
      userId,
      currentSection: 'main_menu',
      context: {},
      navigationStack: [],
    });
  }
  return sessions.get(userId)!;
}

export function pushState(userId: string, section: string, context: Record<string, any> = {}): void {
  const session = getSession(userId);
  session.navigationStack.push({
    section: session.currentSection,
    context: { ...session.context },
  });
  session.currentSection = section;
  session.context = context;
}

export function popState(userId: string): NavigationEntry | null {
  const session = getSession(userId);
  if (session.navigationStack.length === 0) {
    session.currentSection = 'main_menu';
    session.context = {};
    return null;
  }
  const entry = session.navigationStack.pop()!;
  session.currentSection = entry.section;
  session.context = entry.context;
  return entry;
}

export function clearStack(userId: string): void {
  const session = getSession(userId);
  session.currentSection = 'main_menu';
  session.context = {};
  session.navigationStack = [];
}

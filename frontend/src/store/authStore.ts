import { create } from "zustand";
import type { User } from "firebase/auth";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";
import { auth, googleProvider } from "../lib/firebase";
import { createUserDocument } from "../services/userService";

// ---------------------------------------------------------------------------
// Firebase error → human-readable message
// ---------------------------------------------------------------------------
function parseFirebaseError(code: string): string {
  const map: Record<string, string> = {
    "auth/invalid-email":            "The email address is not valid.",
    "auth/user-disabled":            "This account has been disabled.",
    "auth/user-not-found":           "No account found with this email.",
    "auth/wrong-password":           "Incorrect password. Please try again.",
    "auth/email-already-in-use":     "An account with this email already exists.",
    "auth/weak-password":            "Password must be at least 6 characters.",
    "auth/too-many-requests":        "Too many attempts. Please wait and try again.",
    "auth/network-request-failed":   "Network error. Check your connection.",
    "auth/popup-closed-by-user":     "Sign-in popup was closed before completing.",
    "auth/cancelled-popup-request":  "Only one sign-in popup allowed at a time.",
    "auth/invalid-credential":       "Invalid email or password.",
  };
  return map[code] ?? "An unexpected error occurred. Please try again.";
}

// ---------------------------------------------------------------------------
// State shape
// ---------------------------------------------------------------------------
interface AuthState {
  user: User | null;
  loading: boolean;      // true while Firebase resolves initial session
  actionLoading: boolean; // true while a sign-in / sign-up action is in flight
  error: string | null;

  // Actions
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
  clearError: () => void;
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
export const useAuthStore = create<AuthState>()((set) => {
  // Kick off the persistent-session listener as soon as the store is created.
  onAuthStateChanged(auth, (firebaseUser) => {
    set({ user: firebaseUser, loading: false });
  });

  return {
    user: null,
    loading: true,
    actionLoading: false,
    error: null,

    setUser: (user) => set({ user }),
    clearError: () => set({ error: null }),

    // ---- Email / password sign-in ----------------------------------------
    signIn: async (email, password) => {
      set({ actionLoading: true, error: null });
      try {
        const credential = await signInWithEmailAndPassword(auth, email, password);
        // Block navigation until the backend user document is confirmed.
        await createUserDocument(credential.user, "password");
      } catch (err: unknown) {
        const code = (err as { code?: string }).code ?? "";
        if (code) {
          // Firebase auth error
          set({ error: parseFirebaseError(code) });
        } else {
          // Backend user-creation error — sign out so the user isn't left in a
          // half-authenticated state, then surface a message.
          await signOut(auth).catch(() => null);
          set({
            user: null,
            error: (err as Error).message ?? "Account setup failed. Please try again.",
          });
        }
      } finally {
        set({ actionLoading: false });
      }
    },

    // ---- Email / password sign-up ----------------------------------------
    signUp: async (email, password) => {
      set({ actionLoading: true, error: null });
      try {
        const credential = await createUserWithEmailAndPassword(auth, email, password);
        // Block navigation until the backend user document is confirmed.
        await createUserDocument(credential.user, "password");
      } catch (err: unknown) {
        const code = (err as { code?: string }).code ?? "";
        if (code) {
          set({ error: parseFirebaseError(code) });
        } else {
          await signOut(auth).catch(() => null);
          set({
            user: null,
            error: (err as Error).message ?? "Account setup failed. Please try again.",
          });
        }
      } finally {
        set({ actionLoading: false });
      }
    },

    // ---- Google OAuth ----------------------------------------------------
    signInWithGoogle: async () => {
      set({ actionLoading: true, error: null });
      try {
        const result = await signInWithPopup(auth, googleProvider);
        // Block navigation until the backend user document is confirmed.
        await createUserDocument(result.user, "google");
      } catch (err: unknown) {
        const code = (err as { code?: string }).code ?? "";
        if (code === "auth/popup-closed-by-user" || code === "auth/cancelled-popup-request") {
          // User dismissed popup — silent ignore.
        } else if (code) {
          set({ error: parseFirebaseError(code) });
        } else {
          await signOut(auth).catch(() => null);
          set({
            user: null,
            error: (err as Error).message ?? "Account setup failed. Please try again.",
          });
        }
      } finally {
        set({ actionLoading: false });
      }
    },

    // ---- Logout ----------------------------------------------------------
    logout: async () => {
      set({ actionLoading: true, error: null });
      try {
        await signOut(auth);
        set({ user: null });
      } catch (err: unknown) {
        const code = (err as { code?: string }).code ?? "";
        set({ error: parseFirebaseError(code) });
      } finally {
        set({ actionLoading: false });
      }
    },
  };
});

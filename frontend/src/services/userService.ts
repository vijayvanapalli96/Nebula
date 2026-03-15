import type { User } from "firebase/auth";

const BASE_URL = "https://nebula-backend-979585801507.us-central1.run.app";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type UserProvider = "password" | "google";

export interface UserDocument {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL: string | null;
  provider: UserProvider;
  createdAt: string;
  updatedAt: string;
  lastLoginAt: string;
  role: string;
  status: string;
}

// ---------------------------------------------------------------------------
// createUserDocument
//
// Calls POST /api/users/create on the backend.
// Passes the Firebase ID token in the Authorization header so the backend
// can verify the caller's identity and protect against spoofed UIDs.
//
// This is fire-and-forget friendly:
//   createUserDocument(user, "google").catch(console.error);
// ---------------------------------------------------------------------------

export async function createUserDocument(
  user: User,
  provider: UserProvider,
): Promise<UserDocument | null> {
  try {
    // Refresh the token if it's close to expiry; uses Firebase's cache otherwise.
    const idToken = await user.getIdToken();

    const payload = {
      uid:         user.uid,
      email:       user.email ?? "",
      displayName: user.displayName ?? null,
      photoURL:    user.photoURL ?? null,
      provider,
    };

    const res = await fetch(`${BASE_URL}/api/users/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${idToken}`,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({})) as { detail?: string };
      throw new Error(
        errBody.detail ?? `Account setup failed (${res.status} ${res.statusText})`,
      );
    }

    const data = await res.json() as { success: boolean; user: UserDocument };
    return data.user;
  } catch (err) {
    // Re-throw so callers can decide whether to block the auth flow.
    throw err;
  }
}

export interface ErrorResponse {
    error: string;
    message: string;
}

export enum Role {
    user, assistant
}

export interface Message {
    id: `${string}-${string}-${string}-${string}-${string}`;
    role: Role;
    avatar: string;
    content: string;
    summary?: EpisodeSummary;
}

export interface ChunkSummary {
    chunk_number: number;
    title: string;
    summary: string;
    key_events: string[];
    characters: string[];
}

export interface EpisodeSummary {
    title: string;
    final_summary: string;
    key_events: string[];
    characters: string[];
    chunk_summaries: ChunkSummary[];
}

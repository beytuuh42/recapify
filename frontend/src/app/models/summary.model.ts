export interface SummaryRequest {
    title: string;
    season: number;
    episode: number;
    language: string;
}

export enum Role {
    user, assistant
}

export interface Message {
    id: `${string}-${string}-${string}-${string}-${string}`;
    role: Role;
    avatar: string;
    content: string;
}

export interface Summary {
    content: string;
}

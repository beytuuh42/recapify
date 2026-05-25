package com.recapify.llm;

import java.util.List;

public record Chunk(int chunk_number, String title, String summary, List<String> key_events, List<String> characters) {
}

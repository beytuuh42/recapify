package com.recapify.llm;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class LlmService {

    private final WebClient llmServiceWebClient;

    public LlmService(WebClient llmServiceWebClient) {
        this.llmServiceWebClient = llmServiceWebClient;
    }

    public SummaryRequest getIntent(String text) {
        IntentRequest req = new IntentRequest(text);
        return llmServiceWebClient.post().uri(uriBuilder -> uriBuilder.path("/api/v1/intent").queryParam("message", req.message()).build()).retrieve().bodyToMono(SummaryRequest.class).block();
    }

    public Summary getSummary(String text) {
        SummaryRequest summaryRequest = getIntent(text);
        return llmServiceWebClient.post().uri("/api/v1/summarize").bodyValue(summaryRequest).retrieve().bodyToMono(SummaryResponse.class).map(res -> new Summary(res.final_summary())).block();
    }
}

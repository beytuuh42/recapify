package com.recapify.llm;

import com.recapify.llm.client.MlServiceClient;
import com.recapify.llm.dto.SummaryRequest;
import com.recapify.llm.dto.SummaryResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class LlmService {

    private final MlServiceClient mlServiceClient;

    public SummaryRequest getIntent(String text) {
        return mlServiceClient.extractIntent(text);
    }

    public SummaryResponse getSummary(String text) {
        long startedAt = System.nanoTime();
        SummaryRequest summaryRequest = getIntent(text);
        SummaryResponse summary = mlServiceClient.fetchSummary(summaryRequest);
        long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
        log.info("Summary workflow completed finalSummaryLength={} keyEventsCount={} durationMs={}",
                summary.final_summary().length(), summary.key_events().size(), durationMs);
        return summary;
    }
}

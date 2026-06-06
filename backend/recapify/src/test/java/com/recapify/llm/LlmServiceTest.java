package com.recapify.llm;

import com.recapify.llm.client.MlServiceClient;
import com.recapify.llm.dto.SummaryRequest;
import com.recapify.llm.dto.SummaryResponse;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class LlmServiceTest {

    @Test
    void orchestratesIntentThenSummary() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        SummaryRequest intent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        SummaryResponse expectedSummary = new SummaryResponse("Pilot", "Walter starts cooking meth.", List.of(), List.of(), List.of());
        MlServiceClient client = mock(MlServiceClient.class);
        LlmService service = new LlmService(client);
        when(client.extractIntent(prompt)).thenReturn(intent);
        when(client.fetchSummary(intent)).thenReturn(expectedSummary);

        SummaryResponse summary = service.getSummary(prompt);

        assertThat(summary).isEqualTo(expectedSummary);
        verify(client).extractIntent(prompt);
        verify(client).fetchSummary(intent);
    }

    @Test
    void getIntentDelegatesToClient() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        SummaryRequest expectedIntent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        MlServiceClient client = mock(MlServiceClient.class);
        LlmService service = new LlmService(client);
        when(client.extractIntent(prompt)).thenReturn(expectedIntent);

        SummaryRequest intent = service.getIntent(prompt);

        assertThat(intent).isEqualTo(expectedIntent);
        verify(client).extractIntent(prompt);
    }
}

import { v4 as uuidv4 } from 'uuid';
import type { Message } from '../models/summary.model';

export function createMessageId(): Message['id'] {
  return uuidv4() as Message['id'];
}

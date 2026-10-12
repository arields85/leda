import { describe, expect, it } from 'vitest';
import { isAdminDoor } from './door';

describe('isAdminDoor', () => {
  it('opens the administration only under /app/admin', () => {
    expect(isAdminDoor('/app/admin/')).toBe(true);
    expect(isAdminDoor('/app/admin')).toBe(true);
    expect(isAdminDoor('/app/admin/cargar')).toBe(true);
    expect(isAdminDoor('/app/')).toBe(false);
    expect(isAdminDoor('/app/administracion')).toBe(false);
  });
});

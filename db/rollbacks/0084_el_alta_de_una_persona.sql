\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0084_el_alta_de_una_persona.sql: borra las funciones del alta desde la web y vuelve a
-- la columna `activation_token.token`. Las personas dadas de alta o reactivadas y sus cambios del
-- equipo quedan. Los enlaces sin usar dejan de servir: la huella no devuelve el token, así que la
-- columna se llena con la huella (única y no nula, como pide la tabla) y hay que emitirlos de
-- nuevo.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0084 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop function if exists emitir_enlace_de_activacion(text, text, uuid, uuid, text);
drop function if exists reactivar_integrante(text, text, uuid, uuid, uuid, uuid, uuid, text, text);
drop function if exists dar_de_alta(text, text, uuid, text, uuid, uuid, uuid, text, text);
drop function if exists confirmar_alta(text, text, uuid, text, jsonb, text, text);
drop function if exists vista_previa_de_alta(text, text, uuid, text, jsonb);
drop function if exists cambiar_el_alta(uuid, text, jsonb, text);

alter table activation_token add column token text;
update activation_token set token = token_hash;
alter table activation_token alter column token set not null;
alter table activation_token add constraint activation_token_token_key unique (token);
alter table activation_token drop column token_hash;

commit;

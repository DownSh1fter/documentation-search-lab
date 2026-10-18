# Baseline error notes / Разбор ошибок бейзлайна

## English

The TF-IDF baseline returned no labeled relevant passage in the top five for four of 32 development questions. The explanations below are hypotheses based on the question wording and retrieved passages; semantic retrieval will let us compare them.

| ID | Question | Likely lexical-search issue |
| --- | --- | --- |
| q003 | How does an if statement choose which code block to execute? | The query describes a condition in plain language, while the source uses terms such as conditional execution. The token `if` is removed as an English stop word. |
| q013 | How can an if clause filter values inside a list comprehension? | The relevant section describes `if` clauses, but the query's word `filter` does not occur in the passage. Nearby comprehension sections share more query terms. |
| q018 | Where does Python look for a module when importing it? | The source is specifically about the module search path. The query uses `look for` instead of `search path`, and `module` appears throughout the corpus. |
| q024 | How is a syntax error different from an exception raised while a program runs? | The query combines two concepts whose words appear across many error sections. It does not use the source's phrase `parsing error`, so the narrow syntax-error passage is missed. |

These examples show where exact word matching struggles with paraphrases and common terms. The hand-labeled set is small, so we will review the labels before treating the scores as a reliable comparison.

## Русский

TF-IDF-бейзлайн не нашёл ни одного размеченного релевантного фрагмента в первой пятёрке для четырёх из 32 вопросов. Ниже приведены предположения по формулировкам вопросов и найденным фрагментам; сравнить их поможет семантический поиск.

| ID | Вопрос | Вероятная проблема лексического поиска |
| --- | --- | --- |
| q003 | Как оператор if выбирает блок кода для выполнения? | Вопрос описывает условие обычными словами, а в источнике используются термины об условном выполнении. Токен `if` удаляется как английское стоп-слово. |
| q013 | Как условие if фильтрует значения внутри генератора списка? | В нужном разделе говорится об условии `if`, но слова `filter` в тексте нет. Соседние разделы о генераторах списков совпадают с другими словами вопроса лучше. |
| q018 | Где Python ищет модуль при импорте? | Источник посвящён пути поиска модулей. В вопросе используются слова `look for`, а в источнике — `search path`; слово `module` часто встречается во всём корпусе. |
| q024 | Чем синтаксическая ошибка отличается от исключения во время выполнения программы? | В вопросе соединены понятия, слова о которых встречаются во многих разделах про ошибки. В нём нет формулировки `parsing error`, поэтому узкий раздел о синтаксических ошибках не находится. |

Эти примеры показывают, где поиск по точным словам плохо справляется с перефразированием и частыми терминами. Размеченный набор небольшой, поэтому перед серьёзным сравнением проверим метки вручную.

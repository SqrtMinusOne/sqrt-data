drop view if exists "vk"."VkMessageSent";
create view "vk"."VkMessageSent" as
select
      (case when recepient = 'Pavel Korytov' then sender else recepient end) as target,
      (sender = 'Pavel Korytov') as outgoing,
      message,
      date,
      is_edited,
      is_group
    from "vk"."VkMessage" M
    left join vk."VkUser" U ON M.target_id = U.id
order by date
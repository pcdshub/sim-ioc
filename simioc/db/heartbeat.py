from caproto.server import PVGroup, pvproperty


class HeartbeatGroup(PVGroup):
    heartbeat = pvproperty(
        value=0,
        record='bo',
        read_only=True,
        doc='The heartbeat signal',
    )

    beat_id = pvproperty(
        value=0,
        record='longin',
        read_only=True,
        doc='Always-increasing heartbeat ID',
    )

    beat_pattern = pvproperty(
        value=[0, 1, 1, 1, 1, 1],
        max_length=1024,
        doc='0 to skip beat, non-zero to beat',
    )

    @heartbeat.scan(period=0.5, use_scan_field=True)
    async def heartbeat(self, instance, async_lib):
        beat_id = self.beat_id.value + 1
        await self.beat_id.write(beat_id)
        beat_pattern = self.beat_pattern.value
        if not beat_pattern[beat_id % len(beat_pattern)]:
            return

        await instance.write(beat_id % 2)

    @beat_pattern.startup
    async def beat_pattern(self, instance, async_lib):
        scan = self.heartbeat.fields['SCAN']
        await scan.write('.5 second')
